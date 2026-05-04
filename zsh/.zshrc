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

