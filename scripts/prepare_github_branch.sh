#!/usr/bin/env bash
# Import the review branch from the release bundle. Does not push or merge main.
set -euo pipefail
task_script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
task_repo=${1:-/home/dima54/Projects/mira}
task_bundle=${2:-$task_script_dir/MIRA_update.bundle}
task_branch=mira-update-20261028
task_base=24b4428877257387bc5a686abd9e830a37f58770
if [[ ! -f "$task_bundle" ]]; then
  echo 'Не найден MIRA_update.bundle рядом со скриптом. Используйте скрипт из распакованного архива или передайте путь к bundle вторым аргументом.' >&2
  exit 1
fi
cd -- "$task_repo"
task_top=$(git rev-parse --show-toplevel)
cd -- "$task_top"
task_origin=$(git remote get-url origin)
case "$task_origin" in
  https://github.com/max-talanov/mira|https://github.com/max-talanov/mira.git|git@github.com:max-talanov/mira.git|ssh://git@github.com/max-talanov/mira.git) ;;
  *) echo 'Остановлено: origin не указывает на max-talanov/mira. Проверьте выбранную папку.' >&2; exit 1 ;;
esac
if [[ -n "$(git status --porcelain)" ]]; then
  echo 'Остановлено: в репозитории есть незакоммиченные изменения. Сначала сохраните их своим коммитом; файлы не изменены.' >&2
  exit 1
fi
git fetch origin
git cat-file -e "$task_base^{commit}"
git bundle verify "$task_bundle"
task_target=$(git bundle list-heads "$task_bundle" refs/heads/distributed-power | awk '{print $1}')
if [[ ! "$task_target" =~ ^[0-9a-f]{40}$ ]]; then
  echo 'Остановлено: ожидаемая ветка distributed-power не найдена в bundle.' >&2
  exit 1
fi
if git show-ref --verify --quiet "refs/heads/$task_branch"; then
  if [[ "$(git rev-parse "$task_branch")" != "$task_target" ]]; then
    echo 'Остановлено: mira-update-20261028 уже существует и содержит другой коммит. Существующая ветка не изменена.' >&2
    exit 1
  fi
else
  git fetch "$task_bundle" "refs/heads/distributed-power:refs/heads/$task_branch"
fi
git switch "$task_branch"
git log -5 --oneline
echo 'Ветка подготовлена. Проверьте diff, затем выполните: git push -u origin mira-update-20261028'
