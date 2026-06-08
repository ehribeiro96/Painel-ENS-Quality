# 08 Release Candidate Package Report

## Origem do pacote
- O pacote foi gerado a partir de `git archive --format=tar --prefix=Painel-ENS-Quality-RC/ HEAD`.
- Isso garante que o release candidate venha do Git versionado, e não do workspace bruto.

## Staging
- Diretório staging:
  - `exports/final_release_candidate_staging/Painel-ENS-Quality-RC`
- Scan do staging:
  - nenhum arquivo proibido real foi encontrado
  - o único hit foi `infra/hermesops/.env.hml.example`, tratado como placeholder de ambiente

## Tarball e checksum
- Tarball:
  - `exports/final_release_candidate/Painel-ENS-Quality-HML-RC-20260608.tar.gz`
- SHA256:
  - gerado em `exports/final_release_candidate/SHA256SUMS.txt`
  - verificação `sha256sum -c` passou

## Leitura
- O pacote final está limpo no critério de release candidate.
- O conteúdo reflete o baseline rastreado pelo Git, não os untrackeds locais do workspace.

