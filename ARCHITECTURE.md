# 🏗️ Technical Architecture

This document outlines how the automated GitHub Profile updates itself without any external infrastructure or complicated authentication.

## How It Works

The architecture relies on a "Self-Updating Repository" pattern. 
1. GitHub Actions spins up a runner every day at a scheduled time.
2. The Action runs Python scripts that scrape your public contribution graph (using `BeautifulSoup`).
3. The scripts process the data locally and render it into a visually appealing SVG Heatmap (`contrib-heatmap.svg`).
4. The Action uses its default `$GITHUB_TOKEN` to commit the updated SVG back into the same repository, meaning your live profile automatically refreshes!

## 1. Implementation Flow Chart

This diagram illustrates the end-to-end process from forking the repository to the automated daily updates.

```mermaid
flowchart TD
    subgraph User Setup
        A[Fork Repository] --> B[Clone Locally]
        B --> C{Customize Profile}
        C -->|Option 1| D[Generate ASCII Portrait]
        C -->|Option 2| E[Edit README.md Text/Badges]
        D --> F[Commit Changes]
        E --> F
        F --> G[Push to GitHub]
    end

    subgraph Automation Trigger
        G --> H{Enable GitHub Actions}
        H --> I[Manual Dispatch trigger]
        H --> J[Daily Cron trigger]
    end

    subgraph Profile Update Cycle
        I --> K[Run python scripts]
        J --> K
        K --> L[Commit updated SVGs]
        L --> M[Live GitHub Profile Updated!]
    end
    
    style User Setup fill:#232F3E,stroke:#333,stroke-width:2px,color:#fff
    style Automation Trigger fill:#7B42BC,stroke:#333,stroke-width:2px,color:#fff
    style Profile Update Cycle fill:#10B981,stroke:#333,stroke-width:2px,color:#fff
```

## 2. Components Connection Flow Chart

This diagram details exactly how the files in this repository interact with each other and the external GitHub API.

```mermaid
flowchart LR
    subgraph External
        GitHubAPI(GitHub Public Contributions UI)
    end

    subgraph Data Layer
        fetch[scripts/fetch_contributions.py]
        json[(data/contributions.json)]
        GitHubAPI -- Scraped by --> fetch
        fetch -- Writes --> json
    end

    subgraph Rendering Layer
        render[scripts/render_heatmap_svg.py]
        svg(contrib-heatmap.svg)
        json -- Read by --> render
        render -- Generates --> svg
    end

    subgraph Assembly Layer
        readme(README.md)
        svg -. Embedded in .-> readme
        ascii(avi-ascii.svg) -. Embedded in .-> readme
    end

    subgraph Deployment
        action[.github/workflows/update-profile-art.yml]
        action -- Executes --> fetch
        action -- Executes --> render
        action -- Commits --> svg
    end
    
    style External fill:#EF4444,stroke:#333,stroke-width:2px,color:#fff
    style Data Layer fill:#0078D4,stroke:#333,stroke-width:2px,color:#fff
    style Rendering Layer fill:#F59E0B,stroke:#333,stroke-width:2px,color:#fff
    style Assembly Layer fill:#10B981,stroke:#333,stroke-width:2px,color:#fff
    style Deployment fill:#7B42BC,stroke:#333,stroke-width:2px,color:#fff
```

## No Tokens Required
Because the Python script (`fetch_contributions.py`) hits GitHub's unauthenticated public HTML endpoint (`https://github.com/users/USERNAME/contributions`), you don't have to deal with rate-limited APIs, GraphQL queries, or Personal Access Tokens. It just works.
