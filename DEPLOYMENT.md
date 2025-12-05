# GitHub Pages Deployment Instructions

This repository is configured for both **GitBook** and **GitHub Pages** deployment.

## GitHub Pages Setup

### 1. Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** → **Pages**
3. Under **Source**, select:
   - Branch: `main` (or `master`)
   - Folder: `/ (root)`
4. Click **Save**

### 2. Update Configuration

Edit `_config.yml` and update these fields:

```yaml
baseurl: "/ai-llm-red-team-handbook-and-field-manual" # Updated to match GitBook
url: "https://cph-sec.gitbook.io" # Updated to match GitBook
github_username: shiva108 # Your GitHub username
linkedin_username: thorkristiansen # Your LinkedIn username
```

### 3. Access Your Site

After a few minutes, your site will be available at:

```
https://shiva108.github.io/ai-llm-red-team-handbook/
```

### 4. Custom Domain (Optional)

To use a custom domain:

1. Add a `CNAME` file to the root with your domain name
2. Configure DNS settings at your domain registrar
3. Enable HTTPS in GitHub Pages settings

---

## GitBook Setup

### Method 1: GitBook Cloud (Recommended)

1. Go to [gitbook.com](https://www.gitbook.com/)
2. Sign in and click **New Space**
3. Select **Import from GitHub**
4. Choose your repository: `shiva108/ai-llm-red-team-handbook`
5. GitBook will auto-detect `.gitbook.yaml` and `docs/SUMMARY.md` and build your book

### Method 2: GitBook CLI (Local - Legacy)

```bash
# Install GitBook CLI
npm install -g gitbook-cli

# Navigate to your repository
cd ai-llm-red-team-handbook

# Install plugins
gitbook install

# Serve locally
gitbook serve

# Build static site
gitbook build

# The built site will be in _book/ directory
```

### 3. GitBook Plugins & Branding

The repository uses a dual-configuration strategy to support both legacy builds and modern GitBook Cloud SaaS.

#### Branding (Logo & Assets)

- **Asset Location**: `docs/assets/banner.svg`
- **Configuration**:
  - `.gitbook.yaml`: Defines `branding` block pointing to `docs/assets/banner.svg` (for new SaaS builds).
  - `book.json`: Defines `insert-logo` plugin pointing to `assets/banner.svg` (relative to `docs` root).
- **Note**: GitBook Cloud (SaaS) often ignores file-based theming. If the logo does not appear, you must set it manually via **Customize > Look & Feel** in the GitBook Dashboard.

#### Plugins (Legacy)

Defined in `book.json`:

- **search-plus**: Enhanced search
- **copy-code-button**: Copy code blocks
- **github**: GitHub integration
- **prism**: Syntax highlighting
- **page-treeview**: Chapter navigation

To install all plugins:

```bash
gitbook install
```

---

## Configuration Files

| File              | Purpose                    | Platform     |
| ----------------- | -------------------------- | ------------ |
| `_config.yml`     | Jekyll configuration       | GitHub Pages |
| `.gitbook.yaml`   | GitBook integration        | GitBook      |
| `book.json`       | GitBook plugins & settings | GitBook      |
| `docs/SUMMARY.md` | Table of contents          | GitBook      |
| `README.md`       | Homepage                   | Both         |

---

## Formatting & Asset Management

### Images

All images must be placed in `docs/assets/`.
Reference them in markdown as `![Alt Text](assets/image.png)` (from root docs) or `![Alt Text](../assets/image.png)` (from subdirectories like `field_manuals/`).

### Building for Different Formats

#### PDF Export (GitBook)

```bash
gitbook pdf ./ ./handbook.pdf
```

#### eBook Export (GitBook)

```bash
# EPUB
gitbook epub ./ ./handbook.epub

# MOBI
gitbook mobi ./ ./handbook.mobi
```

---

## Customization

### GitHub Pages Theme

Change theme in `_config.yml`:

```yaml
theme: jekyll-theme-cayman # Current
# theme: jekyll-theme-minimal
# theme: jekyll-theme-slate
# theme: jekyll-theme-architect
```

### GitBook Styling

Create custom CSS in `styles/website.css`:

```css
/* Custom styles for GitBook */
.book-summary {
  background: #f7f7f7;
}
```

---

## Troubleshooting

### GitHub Pages not building?

- Check that `_config.yml` is valid YAML
- Ensure your branch name is correct in settings
- Wait 5-10 minutes for first build

### GitBook plugins not working?

```bash
# Clear cache and reinstall
rm -rf node_modules
rm -rf _book
gitbook install
gitbook serve
```

### Links broken?

- Use relative links: `[Chapter 1](docs/Chapter_01.md)`
- Avoid absolute paths
- Test locally before pushing

---

## Next Steps

1. ✅ Push these configuration files to GitHub
2. ✅ Enable GitHub Pages in repository settings
3. ✅ Connect to GitBook cloud (optional)
4. ✅ Customize URLs and branding
5. ✅ Share your published handbook!

---

**Your handbook is now ready for both GitBook and GitHub Pages!** 🎉
