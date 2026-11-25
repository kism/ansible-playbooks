# set PATH so it includes user's private bin if it exists
if [ -d "$HOME/.local/bin" ]; then
    PATH="$HOME/.local/bin:$PATH"
fi

if [[ ! -o interactive ]]; then
    return
fi

# Load colors
autoload -U colors && colors
autoload -U up-line-or-beginning-search
autoload -U down-line-or-beginning-search
zle -N up-line-or-beginning-search
zle -N down-line-or-beginning-search
autoload -U compinit; compinit
zstyle ':completion:*' menu select


# Create prompt
local current_dir="%{$terminfo[bold]$fg[green]%}%~ %{$reset_color%}"
PROMPT="${current_dir}"

# region: history
export HISTFILE="$HOME/.zsh_history"
export HISTSIZE=10000
export SAVEHIST=10000

setopt append_history        # append to HISTFILE, don't overwrite
setopt inc_append_history    # write to HISTFILE immediately (per-command)
setopt hist_fcntl_lock       # safer concurrent history writes
setopt hist_reduce_blanks    # trim extra blanks in commands
## History command configuration, from oh-my-zsh
setopt extended_history       # record timestamp of command in HISTFILE
setopt hist_expire_dups_first # delete duplicates first when HISTFILE size exceeds HISTSIZE
setopt hist_ignore_dups       # ignore duplicated commands history list
setopt hist_ignore_space      # ignore commands that start with space
setopt hist_verify            # show command with history expansion to user before running it
setopt share_history          # share command history data
# endregion

# region: keybinds
# https://en.wikipedia.org/wiki/ANSI_escape_code
# https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
# https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/refs/heads/master/lib/key-bindings.zsh
# Honestly, if you want to know what a keybinding is, sleep 60 and just press the key

# Unbind vi-cmd-mode, I think this is escape
bindkey -r "^["

# Home, end
bindkey "${terminfo[khome]}" beginning-of-line
bindkey "${terminfo[kend]}" end-of-line
bindkey "^[[H" beginning-of-line
bindkey "^[[F" end-of-line


## ctrl+arrows
bindkey "\e[1;5C" forward-word
bindkey "\e[1;5D" backward-word

## alt+arrows
bindkey "^[f" forward-word
bindkey "^[b" backward-word

## Command+arrows
bindkey -r "^E"
bindkey -r "^A"

# delete
bindkey "${terminfo[kdch1]}" delete-char

# backspace
# bindkey -v '^?' backward-delete-char
bindkey "${terminfo[kbs]}" backward-delete-char

## ctrl+delete
bindkey "\e[3;5~" kill-word

## ctrl+backspace
bindkey '^H' backward-kill-word

## ctrl+shift+delete
bindkey "\e[3;6~" kill-line

# Up, down
bindkey "${terminfo[kcuu1]}" up-line-or-beginning-search
bindkey "${terminfo[kcud1]}" down-line-or-beginning-search
## Up, down, God know why, ghostty?
bindkey "^[[A" up-line-or-beginning-search
bindkey "^[[B" down-line-or-beginning-search

# endregion
