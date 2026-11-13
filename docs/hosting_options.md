# Hosting the reporting app somewhere else

Checked official documentation on 13 November 2026. The owner prefers a free host without a ChatGPT URL. The dashboard is plain HTML/CSS/JavaScript, so no rewrite or paid server is required. Cloudflare Pages is now deployed at https://bike-reliability-studio.pages.dev. The site is public and the GitHub repository remains private. The other providers below remain alternatives, not additional deployments.

## Cloudflare Pages: recommended while the repository stays private

Supports private GitHub repositories and automatic updates from Git. Static asset requests are free and unlimited; the Free plan allows 500 builds/month. A free `pages.dev` address is provided, with custom domains optional. An owner account and permission to read the selected repository are needed. Actual configuration: production branch `main`, framework `None`, build command blank, root directory `dashboard`, output directory `.`. Publish the static app only, never the raw-data directories.

Sources: https://developers.cloudflare.com/pages/get-started/git-integration/ ; https://developers.cloudflare.com/pages/platform/limits/ ; https://developers.cloudflare.com/pages/functions/pricing/

## GitHub Pages: simplest if public dashboard source is acceptable

Free hosting from a public repository on GitHub Free. A private source repository requires an eligible paid GitHub plan. The website can use `stephanieboyle.github.io/<project>/`. A separate public repository containing only the reporting app could leave the analysis repository private, but making any source public requires the owner's explicit instruction. No such change has been made.

Source: https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages

## Vercel Hobby: another free personal-project option

The Hobby plan is free for personal, non-commercial use and supports Git-based deployment. It has usage caps and a `vercel.app` address. More platform features than this static dashboard needs; Cloudflare Pages or GitHub Pages are the simpler shortlist. Owner account/connection would be required.

Sources: https://vercel.com/docs/plans/hobby ; https://vercel.com/docs/plans

A public portfolio website can show the dashboard without giving visitors access to the private analysis repository. Any downloadable app assets are visible to website visitors, so only the intended aggregate report belongs in the published folder. A custom domain is optional and would normally have a separate registration cost.
