# How to get your page online

Your site is static HTML/CSS/JS. No build step. Upload the contents of this folder (`www`) to any static host.

## GitHub Pages

1. Create a repo and push the contents of `www` (or put `www` in a branch like `gh-pages`).
2. Repo **Settings** > **Pages** > **Source**: Deploy from branch. Choose branch and `/ (root)` or `/docs` if you use a `docs` folder.
3. Site URL: `https://<username>.github.io/<repo>/`

## Netlify

1. Sign up at [netlify.com](https://netlify.com).
2. **Add new site** > **Deploy manually**: drag and drop the `www` folder, or connect your Git repo and set **Publish directory** to `www`.
3. Optional: add a custom domain in **Domain settings**.

## Vercel

1. Sign up at [vercel.com](https://vercel.com).
2. **Add New** > **Project**: import your Git repo. Set **Root Directory** to the folder that contains `www`, and **Output Directory** to `www` (or use **Other** and upload the folder).
3. Deploy.

## Cloudflare Pages

1. Sign up at [pages.cloudflare.com](https://pages.cloudflare.com).
2. **Create a project** > **Direct Upload**: upload the `www` folder as a zip, or connect Git and set **Build output directory** to `www`.
3. Deploy.

## Any static host

Upload the contents of `www` (all `.html`, `styles.css`, `script.js`) via FTP, SFTP, or your host's file manager. No build or server-side code required.
