# Binding rules for Codex tasks

These rules apply to the entire repository.

## Project boundaries

1. Prefer open-source software and document any justified exceptions.
2. Keep KDE Plasma and EndeavourOS/Arch Linux as the technical foundation.
3. Do not create a custom ISO or Linux distribution.
4. Respect approved architecture decisions. Changes to them must be documented
   as decisions and confirmed by the user.
5. Implement only the explicitly requested scope.

## Security and privacy

1. Never commit passwords, tokens, SSH keys, private keys, credentials, or any
   other secrets.
2. Scan new and changed files for possible secrets before completing a task.
3. Obtain explicit confirmation before destructive actions. Describe the
   target, impact, and recovery options when requesting confirmation.
4. Do not make production system changes unless a later, confirmed task
   explicitly requires them.
5. Do not run commands that overwrite existing user files without confirmation.

## Configuration and implementation

1. Keep general configuration free of hardware-specific values.
2. Store device-specific adjustments only under
   `hardware/profiles/<profile>/`, and activate them only after explicit
   selection.
3. Make installation and configuration scripts idempotent: repeated execution
   must result in the same desired state.
4. Prefer declarative configuration, small understandable steps, and verifiable
   preconditions.
5. Keep package lists separated by source. Do not mix Pacman, AUR, and Flatpak
   packages.
6. Separate GNU Stow packages under `dotfiles/` so they can be enabled
   individually.

## Documentation and validation

1. Describe the actual implementation status accurately. Do not present roadmap
   items, designs, or planned features as implemented.
2. Document new architecture decisions in `docs/decisions.md`.
3. Update the recovery documentation whenever the tested workflow changes.
4. Validate shell scripts with at least `bash -n` and run appropriate,
   non-destructive checks.
5. Before completing a task, review `git diff`, `git status`, and all changed
   content for accidentally included secrets.
6. Do not create commits or push changes without explicit user approval.
