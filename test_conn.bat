Invoke-WebRequest -Uri "http://localhost:8000/api/move"  -Method POST -Body '{"move": "e2e4", "fen": "sample_fen"}' -ContentType "application/json"
