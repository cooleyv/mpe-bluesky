#!/bin/bash

# start a bluesky session in IPython console (default) or Jupyter notebook GUI

# Get the Python environment name.
# either: BLUESKY_CONDA_ENV (with fallback to DEFAULT_ENV)
DEFAULT_ENV=bluesky_2023_2
# DEFAULT_ENV=training_2022
export ENV_NAME="${BLUESKY_CONDA_ENV:-${DEFAULT_ENV}}"
export IPYTHON_PROFILE=bluesky
export IPYTHONDIR="${HOME}/.ipython"


pick () {  # activate ENV_NAME using (conda) from given arg

    ARG="${1}"
    # echo "============"
    # echo "==> ARG=${ARG}"

    if [ "${ARG}" == "" ]; then
        # echo "empty"
        return 1
    fi

    if [ -d "${ARG}" ]; then
        # echo "a directory"

        pick "${ARG}/bin/conda"

        if [ "${cmd_base}" != "" ]; then
            # echo "==> cmd_base = ${cmd_base}"
            return 0
        fi
        return 1
    fi

    CMD=$(which ${ARG})  # as executable command
    if [ "${CMD}" == "" ]; then
        return 1
    fi

    # echo "==> CMD=${CMD}"
    if [ -x "${CMD}" ]; then
        # echo "==> executable cmd = ${CMD}"
        match_env_name=$( \
            ${CMD} env list \
            | grep "^[ ]*${ENV_NAME} " \
            | awk '{print $1}' \
        )
        if [ "${match_env_name}" != "" ]; then
            # found the requested environment name
            cmd_base=$(basename "${CMD}")
            # echo "==> match_env_name cmd = ${match_env_name}"
            case "${cmd_base}" in
                conda | mamba)
                    source "$(dirname ${CMD})/activate" base
                    "${cmd_base}" activate "${ENV_NAME}"
                    # echo "==> CONDA_PREFIX = ${CONDA_PREFIX}"
                    return 0
                    ;;
                *)
                    return 1
                    ;;
            esac
        fi
    fi

    return 2
}


pick_environment_executable () {  # Activate the environment
    # Pick the first "hit"
    pick "/APSshare/miniconda/x86_64" \
    || pick "${HOME}" \
    || pick "conda" \
    || pick "/opt/miniconda3" \
    || pick "${HOME}/Apps/miniconda" \
    || pick "${HOME}/Apps/anaconda"

    echo "==> CONDA_PREFIX=${CONDA_PREFIX}"

    if [ "${cmd_base}" != "" ]; then
        echo "$(which python) -- $(python --version)"
        return 0
    fi

    echo "Could not activate environment: '${ENV_NAME}'"
    return 3
}


console_session () {
    export OPTIONS=""
    export OPTIONS="${OPTIONS} --profile=${IPYTHON_PROFILE}"
    export OPTIONS="${OPTIONS} --ipython-dir=${IPYTHONDIR}"
    export OPTIONS="${OPTIONS} --IPCompleter.use_jedi=False"
    export OPTIONS="${OPTIONS} --InteractiveShellApp.hide_initial_ns=False"

    pick_environment_executable

    ipython ${OPTIONS}
}

lab_server () {
    export OPTIONS=""
    # export OPTIONS="${OPTIONS} --no-browser"
    export OPTIONS="${OPTIONS} --ip=${HOST}"

    pick_environment_executable

    python -m ipykernel install --user --name "${ENV_NAME}"
    jupyter-lab ${OPTIONS}
}

usage () {
    echo $"Usage: $0 [console | lab | help]"
}

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

case $(echo "${1}" | tr '[:upper:]' '[:lower:]') in
  gui | jupyter | lab | notebook | server) lab_server  ;;
  "" | console | ipython) console_session  ;;
  help | usage) usage  ;;
  *) usage; exit 1
esac
