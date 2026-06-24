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
alias zconf="hx ~/.zshrc"
alias zreload="source ~/.zshrc"

# ==========================================
# GITHUB AUTOMATION SHORTCUTS
# ==========================================

# 1. SOLO/PRIVATE PROJECTS: The ultimate lazy mode.
# Automatically stages, commits with a timestamp, and pushes in one shot.
# Usage: just type 'gcap'
alias gcap="git add . && git commit -m \"Auto-update: \$(date +'%Y-%m-%d %H:%M:%S')\" && git push"

# 2. PUBLIC/TEAM PROJECTS: Fast but professional.
# Automatically stages and pushes, but forces you to write a meaningful message.
# Usage: gcm "your custom commit message here"
gcm() {
    git add . && git commit -m "$1" && git push
}
