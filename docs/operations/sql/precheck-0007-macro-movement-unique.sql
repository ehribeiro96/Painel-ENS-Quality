SELECT
    context_type,
    context_id,
    COUNT(*) AS duplicate_count
FROM macro_generations
WHERE context_type = 'asset_movement'
  AND context_id IS NOT NULL
GROUP BY context_type, context_id
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC, context_id;
