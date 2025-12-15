# Makefile
SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c

.DEFAULT_GOAL := help

REMOTE ?= origin

# -----------------------------------------------------------------------------
# Package manager detection ----------------------------------------------------
# -----------------------------------------------------------------------------
ifeq ($(strip $(PACKAGE_MANAGER)),)
  ifneq ($(wildcard pnpm-lock.yaml),)
    PACKAGE_MANAGER := pnpm
  else ifneq ($(wildcard yarn.lock),)
    PACKAGE_MANAGER := yarn
  else
    PACKAGE_MANAGER := npm
  endif
endif

ifeq ($(PACKAGE_MANAGER),pnpm)
  INSTALL_CMD := pnpm install
  RUN_SCRIPT := pnpm
  EXEC_CMD := pnpm
  LOCKFILE ?= pnpm-lock.yaml
  DEPS_CMD := pnpm ls --depth=0
else ifeq ($(PACKAGE_MANAGER),yarn)
  INSTALL_CMD := yarn install --frozen-lockfile
  RUN_SCRIPT := yarn
  EXEC_CMD := yarn
  LOCKFILE ?= yarn.lock
  DEPS_CMD := yarn list --depth=0
else
  PACKAGE_MANAGER := npm
  INSTALL_CMD := npm install
  RUN_SCRIPT := npm run
  EXEC_CMD := npx
  LOCKFILE ?= package-lock.json
  DEPS_CMD := npm ls --depth=0
endif

NODE_MODULES_STAMP := node_modules/.install.stamp

# Helper macro to run a package script
run-script = $(RUN_SCRIPT) $(1)

# Helper used in the "test" target to forward CLI arguments consistently.
ifeq ($(PACKAGE_MANAGER),npm)
  TEST_CMD = CI=1 $(RUN_SCRIPT) test -- $(TEST_ARGS)
else
  TEST_CMD = CI=1 $(RUN_SCRIPT) test $(TEST_ARGS)
endif

TEST_ARGS ?= --watch=false --runInBand

# -----------------------------------------------------------------------------
# High-level project workflows -------------------------------------------------
# -----------------------------------------------------------------------------
.PHONY: help install start build test test-watch clean clean-all format lint deps-info

help: ## Display this help message with the available targets
	@printf "\nAvailable targets (package manager: %s)\n\n" "$(PACKAGE_MANAGER)"
	@awk -F':|##' '/^[a-zA-Z0-9_.-]+:.*##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$NF }' $(MAKEFILE_LIST)

$(NODE_MODULES_STAMP): package.json $(LOCKFILE)
	@echo "📦 Installing dependencies with $(PACKAGE_MANAGER)..."
	@$(INSTALL_CMD)
	@mkdir -p $(dir $@)
	@touch $@

install: $(NODE_MODULES_STAMP) ## Install Node.js dependencies

run: $(NODE_MODULES_STAMP) ## Start the development server
	@$(call run-script,start)

build: $(NODE_MODULES_STAMP) ## Build the production bundle
	@$(call run-script,build)

test: TEST_ARGS := --watch=false --runInBand

test: $(NODE_MODULES_STAMP) ## Run the test suite once in CI-friendly mode
	@$(TEST_CMD)

test-watch: TEST_ARGS :=

test-watch: $(NODE_MODULES_STAMP) ## Run the test suite in watch mode
	@$(TEST_CMD)

lint: $(NODE_MODULES_STAMP) ## Run ESLint if available
	@$(EXEC_CMD) eslint "src/**/*.{ts,tsx,js,jsx}" || echo "(eslint not installed - skipping)"

format: $(NODE_MODULES_STAMP) ## Format code with Prettier if available
	@$(EXEC_CMD) prettier --write "src/**/*.{ts,tsx,js,jsx,json,css,md}" || echo "(prettier not installed - skipping)"

clean: ## Remove build artifacts
	@echo "🧹 Removing build artifacts..."
	rm -rf build

clean-all: clean ## Remove build artifacts and dependencies
	@echo "🧹 Removing node_modules and install stamp..."
	rm -rf node_modules $(NODE_MODULES_STAMP)

deps-info: $(NODE_MODULES_STAMP) ## Print the tree of production dependencies (if available)
	@$(DEPS_CMD) || echo "(dependency tree command unavailable)"

# -----------------------------------------------------------------------------
# Git helpers ------------------------------------------------------------------
# -----------------------------------------------------------------------------
.PHONY: updateGit updateGitNoBackup restoreGit cleanBackups commitGit

updateGit: ## Fetch remote changes and hard reset current branch after creating a backup branch and stash
	BRANCH="$(shell git rev-parse --abbrev-ref HEAD)"
	if [ "$$BRANCH" = "HEAD" ]; then
		echo "❌ You are in a detached HEAD state. Switch to a branch first."
		exit 1
	fi
	echo "➡️  Updating '$$BRANCH' from '$(REMOTE)'..."
	git fetch "$(REMOTE)"
	BACKUP_REF="backup/$$BRANCH-$$(date +%Y%m%d-%H%M%S)"
	echo "💾 Creating backup branch '$$BACKUP_REF'"
	git branch "$$BACKUP_REF"
	echo "📦 Stashing local changes (including untracked files)"
	git stash push --include-untracked -m "pre-updateGit $$BACKUP_REF" >/dev/null || true
	echo "🔁 Resetting to '$(REMOTE)/$$BRANCH' (hard)"
	git reset --hard "$(REMOTE)/$$BRANCH"
	echo "✅ Workspace is now in sync with the remote."

updateGitNoBackup: ## Reset current branch hard to the remote without creating backups
	BRANCH="$(shell git rev-parse --abbrev-ref HEAD)"
	if [ "$$BRANCH" = "HEAD" ]; then
		echo "❌ Detached HEAD. Switch to a branch."
		exit 1
	fi
	git fetch "$(REMOTE)"
	git reset --hard "$(REMOTE)/$$BRANCH"
	echo "✅ Hard reset completed for $(REMOTE)/$$BRANCH."

restoreGit: ## Assist in restoring from previously created backups and stashes
	echo "🔍 Available backup branches:"
	git branch --list "backup/*" || true
	echo
	read -p "Enter the backup branch to restore (leave blank to skip): " BACKUP
	if [ -n "$$BACKUP" ]; then
		echo "🔁 Switching to backup branch '$$BACKUP'..."
		git switch "$$BACKUP"
	else
		echo "⏭️  Skipping branch restoration."
	fi
	echo
	echo "📦 Matching stashes:"
	if ! git stash list | grep pre-updateGit >/dev/null; then
		echo "No matching stash found."
	fi
	read -p "Enter the stash reference to apply (e.g. stash@{0}) or leave blank to skip: " STASH
	if [ -n "$$STASH" ]; then
		echo "🔄 Applying $$STASH..."
		git stash apply "$$STASH"
	else
		echo "⏭️  No stash applied."
	fi
	echo "✅ Restore complete."

cleanBackups: ## Remove all backup branches and stashes created by updateGit
	echo "🧹 Removing backup branches..."
	BRANCHES=$$(git branch --list "backup/*" | tr -d ' *' || true)
	if [ -n "$$BRANCHES" ]; then
		echo "$$BRANCHES" | xargs -r -n1 git branch -D
	else
		echo "No 'backup/*' branches found."
	fi
	echo "🧹 Removing pre-updateGit stashes..."
	STASHES=$$(git stash list --format="%gd %gs" | grep "pre-updateGit" | awk '{print $$1}' || true)
	if [ -n "$$STASHES" ]; then
		echo "$$STASHES" | while read -r ref; do git stash drop "$$ref"; done
	else
		echo "No 'pre-updateGit' stashes found."
	fi
	echo "✅ Cleanup complete."

commitGit: ## Stage all changes, create a commit message template, and push to the configured remote
	BRANCH="$(shell git rev-parse --abbrev-ref HEAD)"
	if [ "$$BRANCH" = "HEAD" ]; then
		echo "❌ Detached HEAD. Switch to a branch."
		exit 1
	fi
	echo "➕ Staging all modifications"
	git add -A
	if git diff --cached --quiet; then
		echo "ℹ️  Nothing to commit."
		exit 0
	fi
	ADDED=$$(git diff --cached --name-only --diff-filter=A | sort || true)
	MODIFIED=$$(git diff --cached --name-only --diff-filter=M | sort || true)
	DELETED=$$(git diff --cached --name-only --diff-filter=D | sort || true)
	RENAMED=$$(git diff --cached --name-status --diff-filter=R | awk '{print $$2 " -> " $$3}' | sort || true)
	TMP_MSG=$$(mktemp)
	cat <<-'MSG' > "$$TMP_MSG"
	$${MSG_PREFIX:-chore}: sync workspace

	$${ADDED:+Added:}
	$${ADDED:+$$(echo "$$ADDED" | sed 's/^/  - /')}

	$${MODIFIED:+Modified:}
	$${MODIFIED:+$$(echo "$$MODIFIED" | sed 's/^/  - /')}

	$${DELETED:+Deleted:}
	$${DELETED:+$$(echo "$$DELETED" | sed 's/^/  - /')}

	$${RENAMED:+Renamed:}
	$${RENAMED:+$$(echo "$$RENAMED" | sed 's/^/  - /')}

	Branch: $$BRANCH  Remote: $(REMOTE)
	Date: $$(date -u +'%Y-%m-%dT%H:%M:%SZ')
	MSG
	echo "📝 Commit message:"
	echo "-----------------"
	cat "$$TMP_MSG"
	echo "-----------------"
	git commit -F "$$TMP_MSG"
	rm -f "$$TMP_MSG"
	if git rev-parse --abbrev-ref "@{u}" >/dev/null 2>&1; then
		echo "📤 Pushing to existing upstream..."
		git push
	else
		echo "📤 Setting upstream and pushing..."
		git push -u "$(REMOTE)" "$$BRANCH"
	fi
	echo "✅ Commit + push complete."


updateFromMain: ## Update From Main branch
	@set -euo pipefail; \
	BRANCH="$$(git rev-parse --abbrev-ref HEAD)"; \
	if [ "$$BRANCH" = "HEAD" ]; then echo "❌ Detached HEAD."; exit 1; fi; \
	echo "➡️  Atualizando '$$BRANCH' com 'origin/main'..."; \
	git fetch origin; \
	git merge origin/main; \
	echo "✅ Branch '$$BRANCH' atualizada com sucesso!"
