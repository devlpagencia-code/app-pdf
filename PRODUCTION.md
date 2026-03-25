# Configuração de Produção

## Storage de PDFs

### Opção 1: Amazon S3 (Recomendado)

1. **Crie um bucket S3** no AWS Console
2. **Configure permissões** para o bucket (política pública ou IAM)
3. **Defina variáveis de ambiente**:

```bash
# .env.prod
STORAGE_TYPE=s3
AWS_S3_BUCKET=meu-bucket-pdf-prod
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=secret...
AWS_REGION=us-east-1
DATABASE_URL=postgresql+psycopg2://user:pass@prod-host:5432/proddb
```

4. **Migre PDFs existentes** (se houver):
```bash
python -m workers.migrate_storage
```

### Opção 2: Filesystem Local

Para servidores únicos ou desenvolvimento:

```bash
# .env
STORAGE_TYPE=local
STORAGE_LOCAL_PATH=/var/app/storage/pdfs
```

**Atenção**: Em containers Docker, monte volume persistente:
```yaml
volumes:
  - ./storage:/var/app/storage
```

## Manutenção Automática

### Agregação de Eventos

Configure cron job para rodar diariamente:

```bash
# Linux/Mac
crontab -e
# Adicione:
0 2 * * * cd /caminho/para/backend && python -m workers.event_aggregator

# Windows Task Scheduler
# Comando: C:\Python\python.exe
# Argumentos: -m workers.event_aggregator
# Pasta inicial: C:\caminho\para\backend
```

### Limpeza de Documentos Antigos

Para limpar PDFs não acessados há 90+ dias:

```bash
# Via API
curl -X POST "http://localhost:8000/api/maintenance/aggregate?cleanup_documents=true&document_retention_days=90"

# Ou via código
from workers.event_aggregator import run_aggregation
run_aggregation(cleanup_documents=True, document_retention_days=90)
```

## Checklist de Produção

- [ ] Configurar `STORAGE_TYPE=s3` e credenciais AWS
- [ ] Migrar PDFs existentes com `migrate_storage.py`
- [ ] Configurar cron job para agregação diária
- [ ] Testar upload e visualização de PDFs
- [ ] Verificar logs de agregação
- [ ] Configurar monitoramento de espaço em disco
- [ ] Backup regular do banco (events + page_analytics)

## Monitoramento

### Espaço em Disco
```sql
-- PostgreSQL: verificar tamanho das tabelas
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Performance
- `events`: deve ter poucos registros (< 7 dias)
- `page_analytics`: cresce devagar (dados históricos)
- `documents`: cresce conforme uploads

### Alertas
- Configurar alertas quando disco > 80%
- Monitorar falhas na agregação via logs