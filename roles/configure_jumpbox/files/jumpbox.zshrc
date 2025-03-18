
# set PATH so it includes user's private bin if it exists
if [ -d "$HOME/.local/bin" ]; then
    PATH="$HOME/.local/bin:$PATH"
fi

if [[ ! -o interactive ]]; then
    return
fi

# Create prompt
local current_dir='%{$terminfo[bold]$fg[green]%}%~ %{$reset_color%}'
PROMPT="${current_dir}"

# region: history
HISTFILE=~/.zsh_history
HISTSIZE=10000
## History command configuration, from oh-my-zsh
setopt extended_history       # record timestamp of command in HISTFILE
setopt hist_expire_dups_first # delete duplicates first when HISTFILE size exceeds HISTSIZE
setopt hist_ignore_dups       # ignore duplicated commands history list
setopt hist_ignore_space      # ignore commands that start with space
setopt hist_verify            # show command with history expansion to user before running it
setopt share_history          # share command history data
# endregion

# region keybinds
# Search with up and down arrows
bindkey "^[[H" beginning-of-line
bindkey "^[[F" end-of-line

## ctrl+arrows
bindkey "\e[1;5C" forward-word
bindkey "\e[1;5D" backward-word

# delete
bindkey "\e[3~" delete-char

## ctrl+delete
bindkey "\e[3;5~" kill-word

## ctrl+backspace
bindkey '^H' backward-kill-word

## ctrl+shift+delete
bindkey "\e[3;6~" kill-line
# endregion

autoload -U compinit; compinit
zstyle ':completion:*' menu select

# Search with up and down arrows
bindkey '^[[A' up-line-or-search
bindkey '^[[B' down-line-or-search
