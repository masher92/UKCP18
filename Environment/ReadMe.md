conda env export --no-builds >env.yml -- didn't work
conda env export --from-history | grep -v prefix > environment.yml -- didn't work
