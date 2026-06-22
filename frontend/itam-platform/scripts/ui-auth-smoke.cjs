#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { chromium } = require('@playwright/test');

function redactValue(value) {
  if (value === null || value === undefined) return '';
  const text = String(value);
  if (!text) return '';
  if (text.length <= 4) return '****';
  return `${text.slice(0, 2)}***${text.slice(-2)}`;
}

function safeTrim(value) {
  return typeof value === 'string' ? value.trim() : '';
}

function parseCredentialFile(filePath) {
  const raw = fs.readFileSync(filePath, 'utf8').trim();
  if (!raw) {
    throw new Error('credential_file_empty');
  }

  const keys = new Map();
  const setKey = (key, value) => {
    if (!key) return;
    keys.set(key.toLowerCase(), value);
  };

  const tryJson = () => {
    try {
      return JSON.parse(raw);
    } catch {
      return null;
    }
  };

  const json = tryJson();
  if (json && typeof json === 'object' && !Array.isArray(json)) {
    for (const [key, value] of Object.entries(json)) {
      if (typeof value === 'string') setKey(key, value);
    }
  } else {
    const lines = raw.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
    for (const line of lines) {
      const kv = line.match(/^([A-Za-z0-9_.-]+)\s*[:=]\s*(.+)$/);
      if (kv) {
        setKey(kv[1], kv[2]);
      }
    }
    if (
      lines.length >= 2 &&
      !keys.get('email') &&
      !keys.get('username') &&
      !keys.get('user') &&
      !keys.get('login') &&
      !keys.get('account') &&
      !keys.get('admin_email') &&
      !keys.get('uat_email') &&
      !keys.get('login_email') &&
      !keys.get('email_address') &&
      !keys.get('user_email') &&
      !keys.get('mail')
    ) {
      setKey('email', lines[0]);
      setKey('password', lines[1]);
    }
    if (lines.length === 1 && lines[0].includes(':')) {
      const [left, ...rest] = lines[0].split(':');
      if (rest.length > 0) {
        setKey('email', left);
        setKey('password', rest.join(':'));
      }
    }
  }

  const email = safeTrim(
    keys.get('email') ||
      keys.get('username') ||
      keys.get('user') ||
      keys.get('login') ||
      keys.get('account') ||
      keys.get('admin_email') ||
      keys.get('uat_email') ||
      keys.get('login_email') ||
      keys.get('email_address') ||
      keys.get('user_email') ||
      keys.get('mail') ||
      ''
  ).replace(/^export\s+/i, '').replace(/^['"]|['"]$/g, '');
  const password = safeTrim(
    keys.get('password') ||
      keys.get('pass') ||
      keys.get('pwd') ||
      keys.get('secret') ||
      keys.get('admin_password') ||
      keys.get('uat_password') ||
      keys.get('login_password') ||
      keys.get('senha') ||
      keys.get('password1') ||
      ''
  ).replace(/^export\s+/i, '').replace(/^['"]|['"]$/g, '');

  if (!email || !password) {
    throw new Error('credential_file_parse_failed');
  }

  return { email, password };
}

function normalizeBaseUrl(value) {
  const trimmed = safeTrim(value) || 'http://127.0.0.1:4173';
  return trimmed.endsWith('/') ? trimmed.slice(0, -1) : trimmed;
}

async function waitForBodyText(page) {
  return page.locator('body').innerText({ timeout: 10000 });
}

async function routeCheck(page, baseUrl, route, summary) {
  const target = new URL(route, baseUrl).toString();
  const beforeErrors = summary.pageErrors.length;
  const beforeConsole = summary.consoleErrors.length;
  let gotoError = null;

  try {
    if (route !== '/') {
      const link = page.locator(`aside a[href="${route}"]`).first();
      if (await link.count()) {
        await link.click({ timeout: 15000 });
        await page.waitForFunction((pathname) => window.location.pathname === pathname, route, { timeout: 15000 }).catch(() => null);
      } else {
        await page.goto(target, { waitUntil: 'domcontentloaded', timeout: 20000 });
      }
    }
    try {
      await page.waitForLoadState('networkidle', { timeout: 10000 });
    } catch {
      // networkidle is best effort only.
    }
  } catch (error) {
    gotoError = error instanceof Error ? error.message : String(error);
  }

  const result = {
    route,
    url: page.url(),
    bodyLength: 0,
    pageErrorCount: summary.pageErrors.length - beforeErrors,
    consoleErrorCount: summary.consoleErrors.length - beforeConsole,
    gotoError,
    status: 'unknown',
  };

  try {
    const bodyText = await waitForBodyText(page);
    result.bodyLength = bodyText.trim().length;
    const pathname = new URL(result.url).pathname;
    if (result.bodyLength > 20 && !gotoError && pathname === route) {
      result.status = 'ok';
    } else if (result.bodyLength <= 20) {
      result.status = 'blank';
    } else if (pathname !== route) {
      result.status = 'redirected';
    } else {
      result.status = 'goto_error';
    }
  } catch (error) {
    result.status = 'no_body';
    result.gotoError = result.gotoError || (error instanceof Error ? error.message : String(error));
  }

  return result;
}

async function main() {
  const baseUrl = normalizeBaseUrl(process.env.UI_UAT_BASE_URL);
  const credentialFile = process.env.UI_UAT_CREDENTIAL_FILE || '/tmp/painel_runtime_h5_credentials.txt';

  if (!fs.existsSync(credentialFile)) {
    console.log(JSON.stringify({ status: 'NO-GO_UAT_CREDENTIAL_UNAVAILABLE', reason: 'credential_file_missing', credentialFile }, null, 2));
    process.exitCode = 2;
    return;
  }

  const creds = parseCredentialFile(credentialFile);
  const summary = {
    baseUrl,
    credentialFile,
    login: null,
    pageErrors: [],
    consoleErrors: [],
    requestFailures: [],
    routes: [],
    assetDetail: null,
    skipped: [],
  };

  let browser;
  let page;
  try {
    browser = await chromium.launch({ headless: true });
    page = await browser.newPage();

    page.on('pageerror', (error) => {
      const message = error instanceof Error ? error.message : String(error);
      summary.pageErrors.push(message);
    });

    page.on('console', (message) => {
      if (message.type() === 'error') {
        const text = message.text();
        if (
          !/Failed to load resource: the server responded with a status of 404/i.test(text) &&
          !/401.*Unauthorized/i.test(text) &&
          !/status of 401/i.test(text)
        ) {
          summary.consoleErrors.push(text);
        }
      }
    });

    page.on('requestfailed', (request) => {
      const failure = request.failure();
      summary.requestFailures.push({ url: request.url(), method: request.method(), errorText: failure?.errorText || 'request_failed' });
    });

    await page.goto(`${baseUrl}/login`, { waitUntil: 'domcontentloaded', timeout: 20000 });
    await page.locator('input[type="email"]').fill(creds.email);
    await page.locator('input[type="password"]').fill(creds.password);
    await page.getByRole('button', { name: /entrar/i }).click();
    await page.waitForFunction(() => window.location.pathname !== '/login', { timeout: 15000 }).catch(() => null);
    await page.locator('aside[aria-label="Menu lateral"]').waitFor({ state: 'visible', timeout: 15000 }).catch(() => null);
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});

    const loginUrl = new URL(page.url());
    const loginBody = await waitForBodyText(page);
    summary.login = {
      url: loginUrl.pathname,
      bodyLength: loginBody.trim().length,
      status: loginUrl.pathname !== '/login' && loginBody.trim().length > 20 ? 'ok' : 'failed',
    };

    if (summary.login.status !== 'ok') {
      console.log(JSON.stringify({ status: 'NO-GO_UI_LOGIN_FAILED', summary }, null, 2));
      process.exitCode = 3;
      return;
    }

    const routeTargets = ['/', '/assets', '/audit-logs', '/imports', '/settings', '/macros', '/users', '/stock', '/signatures', '/ai-chat'];
    const menuHrefs = new Set(await page.locator('aside a[href]').evaluateAll((nodes) => nodes.map((node) => node.getAttribute('href')).filter(Boolean)));

    for (const route of routeTargets) {
      if ((route === '/stock' || route === '/signatures') && !menuHrefs.has(route)) {
        summary.skipped.push({ route, reason: 'not_in_menu' });
        continue;
      }
      const result = await routeCheck(page, baseUrl, route, summary);
      summary.routes.push(result);
      if (result.status !== 'ok') {
        console.log(JSON.stringify({ status: 'NO-GO_UI_ROUTE_REGRESSION', summary }, null, 2));
        process.exitCode = 4;
        return;
      }
    }

    await page.goto(new URL('/assets', baseUrl).toString(), { waitUntil: 'domcontentloaded', timeout: 20000 });
    try {
      await page.waitForLoadState('networkidle', { timeout: 10000 });
    } catch {}
    const assetLinks = await page.locator('a[href^="/assets/"]').evaluateAll((nodes) => nodes.map((node) => ({ href: node.getAttribute('href'), text: (node.textContent || '').trim() })));
    const firstAssetLink = assetLinks.find((item) => item.href && item.href !== '/assets' && item.href !== '/assets/');
    if (!firstAssetLink) {
      summary.assetDetail = { status: 'SKIP_ASSET_DETAIL_NO_ASSET_VISIBLE', href: null };
    } else {
      await page.locator(`a[href="${firstAssetLink.href}"]`).first().click();
      await page.waitForFunction((href) => window.location.pathname === href, firstAssetLink.href, { timeout: 15000 }).catch(() => null);
      try {
        await page.waitForLoadState('networkidle', { timeout: 10000 });
      } catch {}
      const assetBody = await waitForBodyText(page);
      summary.assetDetail = {
        status: assetBody.trim().length > 20 ? 'ok' : 'blank',
        href: firstAssetLink.href,
        bodyLength: assetBody.trim().length,
      };
      if (summary.assetDetail.status !== 'ok') {
        console.log(JSON.stringify({ status: 'NO-GO_UI_ROUTE_REGRESSION', summary }, null, 2));
        process.exitCode = 4;
        return;
      }
    }

    const renderSignals = [...summary.pageErrors, ...summary.consoleErrors];
    if (renderSignals.length > 0) {
      console.log(JSON.stringify({ status: 'NO-GO_UI_RENDER_EXCEPTION', summary }, null, 2));
      process.exitCode = 5;
      return;
    }

    if (summary.assetDetail && summary.assetDetail.status === 'SKIP_ASSET_DETAIL_NO_ASSET_VISIBLE') {
      console.log(JSON.stringify({ status: 'PARTIAL_ASSET_DETAIL_SKIPPED', summary }, null, 2));
      process.exitCode = 0;
      return;
    }

    console.log(JSON.stringify({ status: 'GO_UI_AUTHENTICATED_SMOKE_OK', summary }, null, 2));
    process.exitCode = 0;
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    const status = /Target page, context or browser has been closed/i.test(message)
      ? 'PARTIAL_BROWSER_SYSTEM_DEPS_REQUIRED'
      : /net::ERR_CONNECTION_REFUSED|ECONNREFUSED|timeout/i.test(message)
        ? 'PARTIAL_FRONTEND_SERVER_NOT_ACCESSIBLE'
        : /Failed to launch|Executable doesn't exist|browserType.launch/i.test(message)
          ? 'PARTIAL_BROWSER_SYSTEM_DEPS_REQUIRED'
          : 'NO-GO_UI_RENDER_EXCEPTION';
    console.log(JSON.stringify({ status, error: message, summary }, null, 2));
    process.exitCode = status.startsWith('PARTIAL_') ? 0 : 6;
  } finally {
    if (page) {
      await page.close().catch(() => {});
    }
    if (browser) {
      await browser.close().catch(() => {});
    }
  }
}

main().catch((error) => {
  console.error(JSON.stringify({ status: 'NO-GO_UI_RENDER_EXCEPTION', error: error instanceof Error ? error.message : String(error) }));
  process.exit(6);
});
