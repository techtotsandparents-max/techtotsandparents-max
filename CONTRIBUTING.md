# Contributing Guidelines

Thank you for your interest in contributing to the Automated GitHub Profile architecture! 

Since this repository is designed as a personal profile template, we generally do not accept pull requests that modify the visual layout or add specific personal badges (as these are tailored to the repository owner). 

However, we **highly encourage** contributions that improve the underlying Python automation scripts:

- Enhancing the `fetch_contributions.py` scraper to be more resilient to GitHub HTML changes.
- Optimizing `render_heatmap_svg.py` for smaller file sizes or better color contrast.
- Improving the `make_ascii_svg.py` image processing algorithms.
- Fixing bugs in the GitHub Actions workflow.

## How to Contribute
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/amazing-script-improvement`).
3. Commit your changes (`git commit -m 'feat: improve ascii generation'`).
4. Push to the branch (`git push origin feature/amazing-script-improvement`).
5. Open a Pull Request.

All code contributions should follow standard Python PEP 8 conventions.
