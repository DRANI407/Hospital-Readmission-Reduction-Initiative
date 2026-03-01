# Push This Project to GitHub

Repo: **https://github.com/DRANI407/Hospital-Readmission-Reduction-Initiative**

---

## Option 1: HTTPS + Personal Access Token

If you get **authentication errors**, use a token instead of your GitHub password:

1. Go to **GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)**
2. Click **Generate new token (classic)**
3. Name it (e.g. `Hospital-Readmission-Push`), set expiration, check scope **`repo`**
4. Generate and **copy the token** (starts with `ghp_`)
5. When Git prompts for a password, **paste the token** (not your GitHub password)

Then run:

```bash
cd "/Users/deepz/Downloads/diabetes+130-us+hospitals+for+years+1999-2008 (4)"
git remote set-url origin https://github.com/DRANI407/Hospital-Readmission-Reduction-Initiative.git
git push -u origin main
```

---

## Option 2: GitHub CLI

If you have [GitHub CLI](https://cli.github.com/) installed:

```bash
gh auth login
# Follow prompts: GitHub.com → HTTPS → Login with browser

cd "/Users/deepz/Downloads/diabetes+130-us+hospitals+for+years+1999-2008 (4)"
gh repo create Hospital-Readmission-Reduction-Initiative --public --source=. --remote=origin --push
```

If the repo already exists and you just want to push:

```bash
cd "/Users/deepz/Downloads/diabetes+130-us+hospitals+for+years+1999-2008 (4)"
git remote add origin https://github.com/DRANI407/Hospital-Readmission-Reduction-Initiative.git 2>/dev/null || true
git push -u origin main
```

---

## Large push / HTTP 400

If push fails with `HTTP 400` or "remote hung up", increase the buffer then retry:

```bash
git config http.postBuffer 524288000
git push -u origin main
```

If the remote has different commits (e.g. initial README):

```bash
git push -u origin main --force
```
