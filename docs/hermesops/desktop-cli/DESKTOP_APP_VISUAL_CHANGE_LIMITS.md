# Limites de mudança visual do Desktop App

- O HermesOps não altera automaticamente a interface visual do Hermes Desktop App.
- O Desktop App lê o mesmo core/config/sessões/skills/memória do Hermes, mas novos painéis visuais exigem alteração no código-fonte do app.
- A mudança real nesta fase é abrir o Desktop com `--cwd /home/ribeiro/Build_Mod/HermesOps`, criar comando `hermesops`, criar launcher dedicado, criar atalho dedicado e expor Composio no CLI do HermesOps.
- Para aparecer como aba ou botão "Plugins / Composio" dentro do app, será necessária fase futura com source do Desktop App, branch, build, teste e pacote.
