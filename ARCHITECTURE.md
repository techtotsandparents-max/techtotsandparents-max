# 🏗️ Technical Architecture

This document outlines how the automated GitHub Profile updates itself without any external infrastructure or complicated authentication.

## How It Works

The architecture relies on a "Self-Updating Repository" pattern. 
1. GitHub Actions spins up a runner every day at a scheduled time.
2. The Action runs Python scripts that scrape your public contribution graph (using `BeautifulSoup`).
3. The scripts process the data locally and render it into a visually appealing SVG Heatmap (`contrib-heatmap.svg`).
4. The Action uses its default `$GITHUB_TOKEN` to commit the updated SVG back into the same repository, meaning your live profile automatically refreshes!

## Diagram

```mermaid
flowchart TD
    subgraph GitHub_Actions [GitHub Actions (Runs Daily)]
        A(Trigger: cron 03:17 UTC) --> B(Checkout Repository)
        B --> C[Setup Python 3.12]
        C --> D[Install Dependencies]
    end

    subgraph Python_Data_Layer [Python Generation Layer]
        D --> E{Fetch Contributions}
        E -- Scrapes github.com --> F[(data/contributions.json)]
        
        F --> G[render_heatmap_svg.py]
        G --> H(contrib-heatmap.svg)
        
        I[prep_photo.py] -. Run Manually .-> J[make_ascii_svg.py]
        J -.-> K(avi-ascii.svg)
    end

    subgraph Live_Profile [Live GitHub Profile]
        L(README.md)
        L -. Embeds .-> H
        L -. Embeds .-> K
    end

    subgraph Deployment [Deployment to Self]
        H --> M[Git Add & Commit]
        M --> N[Git Push via Default GITHUB_TOKEN]
        N --> L
    end
    
    style GitHub_Actions fill:#232F3E,stroke:#333,stroke-width:2px,color:#fff
    style Python_Data_Layer fill:#0078D4,stroke:#333,stroke-width:2px,color:#fff
    style Deployment fill:#10B981,stroke:#333,stroke-width:2px,color:#fff
    style Live_Profile fill:#7B42BC,stroke:#333,stroke-width:2px,color:#fff
```

## No Tokens Required
Because the Python script (`fetch_contributions.py`) hits GitHub's unauthenticated public endpoint (`https://github.com/users/USERNAME/contributions`), you don't have to deal with rate-limited APIs, GraphQL queries, or Personal Access Tokens. It just works.
