(function initEnsSignatureCopy(globalScope) {
  "use strict";

  function detectCopyMode() {
    try {
      var params = new URLSearchParams(globalScope.location.search || "");
      var forced = (params.get("copy_mode") || "").trim().toLowerCase();
      if (forced === "outlook_desktop" || forced === "new_outlook_desktop") {
        return "outlook_desktop";
      }
      if (forced === "default" || forced === "padrao") {
        return "default";
      }
    } catch (_err) {
      /* ignore */
    }

    var ua = (globalScope.navigator.userAgent || "").toLowerCase();
    var platform = (globalScope.navigator.platform || "").toLowerCase();
    var brands = "";
    try {
      var list = globalScope.navigator.userAgentData && Array.isArray(globalScope.navigator.userAgentData.brands)
        ? globalScope.navigator.userAgentData.brands
        : [];
      brands = list.map(function mapBrand(item) { return (item && item.brand ? item.brand : ""); }).join(" ").toLowerCase();
    } catch (_err2) {
      brands = "";
    }

    var base = ua + " " + brands;
    var isWindows = platform.indexOf("win") !== -1 || base.indexOf("windows") !== -1;
    var hasOutlook = base.indexOf("outlook") !== -1 || base.indexOf("new outlook") !== -1 || base.indexOf("olk") !== -1;
    var hasOfficeWebView = (base.indexOf("office") !== -1 || base.indexOf("microsoft office") !== -1)
      && (base.indexOf("wv") !== -1 || base.indexOf("webview") !== -1);
    return isWindows && (hasOutlook || hasOfficeWebView) ? "outlook_desktop" : "default";
  }

  function extractSignatureFragment(html) {
    var raw = (html || "").trim();
    if (!raw) {
      return "";
    }
    var host = globalScope.document.createElement("div");
    host.innerHTML = raw;
    var table = host.querySelector("table");
    return table ? (table.outerHTML || raw) : raw;
  }

  function htmlToText(html) {
    var div = globalScope.document.createElement("div");
    div.innerHTML = html || "";
    return (div.innerText || div.textContent || "").replace(/\u00A0/g, " ");
  }

  function buildClipboardHtmlDocument(fragmentHtml) {
    var fragment = (fragmentHtml || "").trim();
    return (
      "<html><head><meta charset='utf-8'></head><body><!--StartFragment-->" +
      fragment +
      "<!--EndFragment--></body></html>"
    );
  }

  function copyViaClipboardEvent(htmlPayload, plainText) {
    var captured = false;
    var input = globalScope.document.createElement("textarea");
    input.value = plainText || " ";
    input.setAttribute("readonly", "readonly");
    input.style.position = "fixed";
    input.style.left = "-9999px";
    input.style.top = "0";
    input.style.opacity = "0";
    globalScope.document.body.appendChild(input);
    input.focus();
    input.select();

    var listener = function onCopy(ev) {
      if (!ev.clipboardData) {
        return;
      }
      ev.preventDefault();
      ev.clipboardData.setData("text/html", htmlPayload);
      ev.clipboardData.setData("text/plain", plainText || "");
      captured = true;
    };

    globalScope.document.addEventListener("copy", listener, true);
    var ok = false;
    try {
      ok = globalScope.document.execCommand("copy");
    } finally {
      globalScope.document.removeEventListener("copy", listener, true);
      globalScope.document.body.removeChild(input);
    }
    return ok && captured;
  }

  async function copyViaNavigator(htmlPayload, plainText) {
    if (!(globalScope.navigator.clipboard && globalScope.navigator.clipboard.write && globalScope.ClipboardItem)) {
      return false;
    }
    var item = new globalScope.ClipboardItem({
      "text/html": new Blob([htmlPayload], { type: "text/html" }),
      "text/plain": new Blob([plainText || ""], { type: "text/plain" })
    });
    await globalScope.navigator.clipboard.write([item]);
    return true;
  }

  function copyViaDomSelection(fragmentHtml) {
    var div = globalScope.document.createElement("div");
    div.contentEditable = "true";
    div.style.position = "fixed";
    div.style.left = "-9999px";
    div.style.top = "0";
    div.style.opacity = "0";
    div.innerHTML = fragmentHtml;
    globalScope.document.body.appendChild(div);
    var range = globalScope.document.createRange();
    range.selectNodeContents(div);
    var selection = globalScope.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);
    var ok = globalScope.document.execCommand("copy");
    selection.removeAllRanges();
    globalScope.document.body.removeChild(div);
    return !!ok;
  }

  async function copyRichHtml(html, options) {
    var opts = options || {};
    var mode = opts.mode || detectCopyMode();
    var fragment = extractSignatureFragment(html);
    if (!fragment) {
      return { ok: false, mode: mode, method: "none", reason: "empty_html" };
    }

    var htmlDocument = buildClipboardHtmlDocument(fragment);
    var htmlPayload = htmlDocument;
    var text = htmlToText(fragment);

    if (mode === "outlook_desktop") {
      // No modo dedicado evitamos fallback degradado para preservar fidelidade no New Outlook Desktop.
      try {
        if (await copyViaNavigator(htmlPayload, text)) {
          return { ok: true, mode: mode, method: "navigator_clipboard", reason: "" };
        }
      } catch (_err1) {
        /* continue */
      }

      try {
        if (copyViaClipboardEvent(htmlPayload, text)) {
          return { ok: true, mode: mode, method: "clipboard_event", reason: "" };
        }
      } catch (_err2) {
        /* continue */
      }

      return { ok: false, mode: mode, method: "none", reason: "strict_outlook_desktop_failed" };
    }

    try {
      if (copyViaClipboardEvent(htmlPayload, text)) {
        return { ok: true, mode: mode, method: "clipboard_event", reason: "" };
      }
    } catch (_err3) {
      /* continue */
    }

    try {
      if (await copyViaNavigator(htmlPayload, text)) {
        return { ok: true, mode: mode, method: "navigator_clipboard", reason: "" };
      }
    } catch (_err4) {
      /* continue */
    }

    try {
      if (copyViaDomSelection(fragment)) {
        return { ok: true, mode: mode, method: "dom_selection", reason: "" };
      }
    } catch (_err5) {
      /* continue */
    }

    return { ok: false, mode: mode, method: "none", reason: "all_methods_failed" };
  }

  globalScope.EnsSignatureCopy = {
    detectCopyMode: detectCopyMode,
    extractSignatureFragment: extractSignatureFragment,
    buildClipboardHtmlDocument: buildClipboardHtmlDocument,
    copyRichHtml: copyRichHtml
  };
})(window);
