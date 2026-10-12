# CareSync — Git & GitHub Version Control Guide

This guide covers Version Control concepts, branching strategies, and exact commands for **23IT723 DevOps Laboratory Experiments 1, 2, and 3**.

---

## 1. Branching Strategy

CareSync follows the **GitFlow** branching model:

```
main (Production releases, tags)
  ▲
  │ (Release / PR Merge)
develop (Integration branch)
  ▲
  ├── feature/appointment-booking (New feature development)
  ├── feature/queue-management
  └── bugfix/duplicate-slot-check (Bug fixes)
```

- **`main`**: Production-ready, stable codebase. Deployed to staging/production via Jenkins.
- **`develop`**: Central integration branch for ongoing development. CI tests run on every push.
- **`feature/<feature-name>`**: Branched from `develop`. Used for isolated feature work. Merged back to `develop` via pull requests.
- **`bugfix/<bug-name>`**: Branched from `develop` (or `main` as `hotfix/*`) to resolve defects.

---

## 2. Fundamental Git Commands & Workflow

### A. Initializing and Checking Status
```bash
# Initialize a new local Git repository
git init

# View working tree status (untracked, modified, staged files)
git status

# Inspect full commit history with graph
git log --oneline --graph --decorate --all
```

### B. Staging & Committing Changes
```bash
# Stage specific file or all files
git add .

# Create a meaningful, conventional commit
git commit -m "feat(appointments): add double booking validation and slot calculation"
```

### C. Remote Repository Management
```bash
# View existing configured remotes
git remote -v

# Link local repository to your remote GitHub repository
git remote add origin https://github.com/<your-username>/caresync-devops.git

# Rename default branch to main if needed
git branch -M main

# Push main branch to GitHub and set upstream tracking
git push -u origin main
```

### D. Synchronizing: Fetch vs Pull
- **`git fetch`**: Downloads new commits, branches, and tags from remote without modifying your local working files.
- **`git pull`**: Performs `git fetch` immediately followed by `git merge FETCH_HEAD` to update the current working branch.

```bash
# Download latest remote references safely
git fetch origin

# Compare local main against fetched remote main
git log HEAD..origin/main --oneline

# Merge changes into current local branch
git merge origin/main

# Or fetch and merge in a single command
git pull origin main
```

---

## 3. Branching, Merging & Practical Conflict Resolution

### Step 1: Create and Switch to Integration Branch
```bash
git checkout -b develop
git push -u origin develop
```

### Step 2: Create a Feature Branch
```bash
git checkout -b feature/doctor-notes
```

Make your edits in `app/models.py`, then commit:
```bash
git add app/models.py
git commit -m "feat: add doctor notes field to appointments model"
```

### Step 3: Fast-Forward or Non-Fast-Forward Merge
Switch back to `develop` and merge the completed feature:
```bash
git checkout develop
git merge --no-ff feature/doctor-notes -m "merge: incorporate feature/doctor-notes into develop"
git branch -d feature/doctor-notes
```

---

## 4. Practical Merge Conflict Simulation & Resolution (Experiment 3)

During lab evaluation, you can demonstrate conflict resolution using this guaranteed reproduction:

### Scenario Setup:
```bash
# 1. Create a demo file on develop
git checkout develop
echo "CareSync Emergency Contact: 911" > emergency.txt
git add emergency.txt
git commit -m "docs: add base emergency contact"

# 2. Branch A: updates contact to Hospital Reception
git checkout -b branch-reception
echo "CareSync Emergency Contact: +1-800-555-RECEPTION" > emergency.txt
git commit -am "update emergency number to reception"

# 3. Branch B: updates same line to Ambulance Hotline
git checkout develop
git checkout -b branch-ambulance
echo "CareSync Emergency Contact: +1-800-555-AMBULANCE" > emergency.txt
git commit -am "update emergency number to ambulance"

# 4. Merge Branch A into develop (succeeds cleanly)
git checkout develop
git merge branch-reception

# 5. Merge Branch B into develop (TRIGGERS CONFLICT!)
git merge branch-ambulance
```

### Conflict Output:
```
CONFLICT (content): Merge conflict in emergency.txt
Automatic merge failed; fix conflicts and then commit the result.
```

### Step-by-Step Resolution:
Open `emergency.txt`. Git annotates the conflicting file with conflict markers:
```text
<<<<<<< HEAD
CareSync Emergency Contact: +1-800-555-RECEPTION
=======
CareSync Emergency Contact: +1-800-555-AMBULANCE
>>>>>>> branch-ambulance
```

Edit `emergency.txt` to the resolved combined version:
```text
CareSync Emergency Contact: +1-800-555-RECEPTION / Ambulance: +1-800-555-AMBULANCE
```

Finalize the resolution:
```bash
git add emergency.txt
git commit -m "fix(merge): resolve emergency contact conflict between reception and ambulance"
```

Verify clean tree:
```bash
git status
# Output: nothing to commit, working tree clean
```
