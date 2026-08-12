# dotfiles

My personal dotfiles for Arch Linux — Hyprland, Kitty, Zsh.

## 📂 Structure

```
.
├── .config/
│   ├── hypr/       # Hyprland window manager config
│   └── kitty/      # Kitty terminal config
├── .zshrc          # Zsh shell config
└── explicit-pkgs.txt   # Explicitly installed packages
```

## 🚀 Setup

```bash
git clone https://github.com/arcanesandip/dotfiles.git
cd dotfiles
cp -r .config ~/.config
cp .zshrc ~/.zshrc
```

Install packages listed in `explicit-pkgs.txt`:

```bash
sudo pacman -S --needed - < explicit-pkgs.txt
```

## 🛠️ Stack

- **WM:** Hyprland
- **Terminal:** Kitty
- **Shell:** Zsh

## 📜 License

MIT — see [LICENSE](./LICENSE).
