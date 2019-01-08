#!/usr/bin/env bash

# Build all permutations of third party libraries used by fornax


LIBRARIES="google_benchmark cares flatbuffers gflags protobuf zlib openssl grpc bzip2 zmq cppzmq fmt tbb boost websocketpp"
HEADER_ONLY="eigen json spdlog catch2"

RECIPE_DIR=$(dirname "$0")
RECIPE_DIR=$(realpath ${RECIPE_DIR})

KAPILSH_REPO=kapilsh/release

SKIP_HEADER_ONLY=0
SKIP_LIBS=0
GCC_ONLY=0

for arg in "$@"
do
    case "$arg" in
            --skip-header-only) ;&
            -H)
                SKIP_HEADER_ONLY=1
                ;;
            --skip-libraries) ;&
            -L)
                SKIP_LIBS=1
                ;;
            --gcc-only) ;&
            -G)
                GCC_ONLY=1
                ;;
            -h) ;&
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  -H --skip-header-only    :     SKip Header Only"
                echo "  -L --skip-libraries      :     SKip Libraries"
                exit 0
                ;;
        esac
done

if [ ${GCC_ONLY} -eq 1 ]
then
    echo "======================================================="
    echo "BUILDING GCC"
    echo "======================================================="

    cd ${RECIPE_DIR}/gcc
    conan export . ${KAPILSH_REPO} || exit 1
    PKG_NAME="gcc/$(cat ${RECIPE_DIR}/gcc/VERSION.txt)@${KAPILSH_REPO}"
    conan install ${PKG_NAME} --build gcc || exit 1
    exit 0
fi

if [ ${SKIP_HEADER_ONLY} -eq 0 ]
then
    for P in ${HEADER_ONLY}
    do
        echo "======================================================="
        echo "BUILDING HEADER ONLY ${P} "
        echo "======================================================="

        cd ${RECIPE_DIR}/${P}
        conan export . ${KAPILSH_REPO} || exit 1
        PKG_NAME="${P}/$(cat ${RECIPE_DIR}/${P}/VERSION.txt)@${KAPILSH_REPO}"
        conan install ${PKG_NAME} --build ${P} || exit 1
    done
fi


if [ ${SKIP_LIBS} -eq 0 ]
then
    for P in ${LIBRARIES}
    do
        echo "======================================================="
        echo "BUILDING LIBRARY ${P} "
        echo "======================================================="

        cd ${RECIPE_DIR}/${P}
        conan export . ${KAPILSH_REPO} || exit 1
        for BT in Release
        do
            PKG_NAME="${P}/$(cat ${RECIPE_DIR}/${P}/VERSION.txt)@${KAPILSH_REPO}"
            conan install ${PKG_NAME} --build ${P} \
                -sbuild_type=${BT} \
                --profile=../build.profile || exit 1
        done
    done
fi


cd ${RECIPE_DIR}
