# Checklist de Aprovação Humana - Migração Docker Engine Nativo

Antes de qualquer migração real:

- [ ] Aprovação do responsável técnico
- [ ] Janela de manutenção definida
- [ ] Docker Desktop atual documentado
- [ ] Context atual documentado
- [ ] Backup lógico Postgres executado e validado
- [ ] Estratégia Qdrant validada
- [ ] Estratégia Redis decidida
- [ ] Compose validado no daemon alvo
- [ ] Portas alternativas definidas, se necessário
- [ ] Rollback revisado
- [ ] `down -v` proibido
- [ ] Secrets fora do Git
- [ ] Logs sanitizados
- [ ] Critério de sucesso aceito
- [ ] Critério de parada aceito
