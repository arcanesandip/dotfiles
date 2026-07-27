# --- BASIC SETUP ---
eval "$(zoxide init zsh)"
export COLORTERM=truecolor
alias hx='helix'
alias vsc='codium'

# --- THE PROMPT (Left Side) ---
# Always shows your folder in cyan
PROMPT='%F{cyan}[%1d]%f %# '

# --- THE STATUS (Right Side) ---
# Shows a green 'OK' or a red 'ERR:code'
RPROMPT='%(?.%F{green}OK%f.%F{red}ERR:%?%f)'

# --- COLORS & COMPLETION ---
alias ls='ls --color=auto'
alias grep='grep --color=auto'

autoload -U compinit && compinit
zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"

# Config Management
alias nconf="nano ~/.zshrc"
alias nreload="source ~/.zshrc"

# ==========================================
# GITHUB AUTOMATION SHORTCUTS
# ==========================================

unalias gcap 2>/dev/null

gcap() {
    # Local project script takes priority, then a scripts/ folder,
    # then your home scripts dir, then a plain fallback.
    if [[ -f "./git-scribe.py" ]]; then
        python3 ./git-scribe.py
    elif [[ -f "./scripts/git-scribe.py" ]]; then
        python3 ./scripts/git-scribe.py
    elif [[ -f "$HOME/scripts/git-scribe.py" ]]; then
        python3 "$HOME/scripts/git-scribe.py"
    else
        git add . && git commit -m "Auto-update: $(date +'%Y-%m-%d %H:%M:%S')" && git push
    fi
}

gcm() {
    if [[ -z "$1" ]]; then
        echo "Usage: gcm \"commit message\""
        return 1
    fi
    git add . && git commit -m "$1" && git push
}
