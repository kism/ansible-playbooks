source ~/.antigen/antigen.zsh

# Load the oh-my-zsh's library.
antigen use oh-my-zsh

# Bundles from the default repo (robbyrussell's oh-my-zsh).
antigen bundle command-not-found

# Syntax highlighting bundle.
antigen bundle zsh-users/zsh-syntax-highlighting

# Create prom[t]
local current_dir='%{$terminfo[bold]$fg[green]%}%~ %{$reset_color%}'
PROMPT="${current_dir}"

# Tell Antigen that you're done.
antigen apply

# Alias
alias please='sudo $(fc -ln -1)'
alias sudp='sudo'
alias tmux='tmux -u'
alias sl='ls'
alias nano='vim'
alias bim='echo -e "\033[0;31m\033[0;41mB\033[0mim"'
alias screen='echo no #'
alias cgrep='grep --color=always -e "^" -e'
alias youtube-dl='yt-dlp -o "%(upload_date)s %(title)s [%(id)s].%(ext)s"'

# SSH
eval `ssh-agent` && ssh-add

# set PATH so it includes user's private bin if it exists
if [ -d "$HOME/.local/bin" ] ; then
    PATH="$HOME/.local/bin:$PATH"
fi

# Keybinds
## ctrl+arrows
bindkey "\e[1;5C" forward-word
bindkey "\e[1;5D" backward-word
### urxvt
bindkey "\eOc" forward-word
bindkey "\eOd" backward-word

## ctrl+delete
bindkey "\e[3;5~" kill-word
### urxvt
bindkey "\e[3^" kill-word

## ctrl+backspace
bindkey '^H' backward-kill-word

## ctrl+shift+delete
bindkey "\e[3;6~" kill-line
### urxvt
bindkey "\e[3@" kill-line
