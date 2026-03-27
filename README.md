# AI-põhine nõustamisplatvorm Eesti väikeettevõtjatele

## Käivitamine

### 1. Mine backendi kausta

```bash
cd backend
```

### 2. Loo virtuaalkeskkond

```bash
python -m venv venv
```

### 3. Aktiveeri virtuaalkeskkond

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Paigalda sõltuvused

```bash
pip install -r requirements.txt
```

### 5. Lisa `.env` faili API võti

```env
OPENAI_API_KEY=your_api_key_here
```

### 6. Käivita server

```bash
uvicorn app.main:app --reload
```

### 7. Ava brauseris

```text
http://127.0.0.1:8000/docs
```