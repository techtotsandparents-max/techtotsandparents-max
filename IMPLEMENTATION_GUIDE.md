# 🚀 How to Build Your Own Automated GitHub Profile

Welcome! If you are here from my YouTube tutorial, this guide will walk you through exactly how to set up this automated, self-updating GitHub profile architecture for yourself.

## What is this?
This repository is a **self-contained automation engine**. It uses GitHub Actions to run a daily Python script that fetches your GitHub contribution data, generates a beautiful heatmap SVG, and commits it back to your profile so it's always up to date.

## Step-by-Step Implementation Guide

### Step 1: Create Your Profile Repository
If you don't already have one, create a new public repository named **exactly after your GitHub username** (e.g., if your username is `johndoe`, create a repository named `johndoe`).

### Step 2: Copy the Architecture
1. Download or copy all the files from this repository into your newly created profile repository. 
   - Specifically, you need the `scripts/` folder, the `data/` folder, `.github/workflows/update-profile-art.yml`, and `README.md`.

### Step 3: Customize Your Content
1. **The ASCII Portrait**: If you want your own photo as ASCII art, place a square portrait of yourself in the root directory named `source-photo.jpg`. Run the background removal and ASCII generation scripts locally (`python scripts/prep_photo.py` then `python scripts/make_ascii_svg.py`), then commit the generated `avi-ascii.svg`.
2. **The Markdown Layout**: Open `README.md` and replace my placeholder text, YAML system info block, and titles with your own details.
3. **The Tech Stack Badges**: Customize the Shields.io badges in the README to reflect your own skills.

### Step 4: Enable GitHub Actions
Because everything is self-contained, you **do not** need to configure any complicated Personal Access Tokens (PATs) for this basic setup to work!

1. Go to the **Actions** tab in your repository.
2. If prompted, click **"I understand my workflows, go ahead and enable them"**.
3. Select the **Update Profile Art** workflow on the left side.
4. Click **Run workflow**.

### You're Done! 🎉
The workflow will now run. It will execute the Python scripts to fetch your public contribution data, generate `contrib-heatmap.svg`, and commit it to your repository. It will automatically run every night at midnight to keep your streak and heatmap up to date!

---
*Created by [Rahul Tripathi](https://github.com/techtotsandparents-max) — Principal Cloud & Systems Architect.*
