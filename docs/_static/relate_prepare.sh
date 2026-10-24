#!/usr/bin/env bash
# Prepare one phased, single-population chromosome for Relate inference.
set -euo pipefail

: "${RELATE_ROOT:?Set RELATE_ROOT to the Relate installation directory}"
: "${ANCESTOR:?Set ANCESTOR to the chromosome ancestral FASTA}"
: "${MAP:?Set MAP to the chromosome genetic map}"
: "${POP_SIZE:?Set POP_SIZE to the initial effective population size}"
: "${MUTATION_RATE:?Set MUTATION_RATE in mutations per bp per generation}"
prefix=${1:?Usage: bash relate_prepare.sh VCF_PREFIX_WITHOUT_EXTENSION}

"$RELATE_ROOT/bin/RelateFileFormats" \
    --mode ConvertFromVcf \
    --haps "$prefix.haps" \
    --sample "$prefix.sample" \
    -i "$prefix"

# Keep individual IDs and order from the converted diploid .sample file.
printf 'sample population group sex\n' > "$prefix.poplabels"
awk 'NR > 2 {print $1, "group1", "group1", "NA"}' \
    "$prefix.sample" >> "$prefix.poplabels"

bash "$RELATE_ROOT/scripts/PrepareInputFiles/PrepareInputFiles.sh" \
    --haps "$prefix.haps" \
    --sample "$prefix.sample" \
    --poplabels "$prefix.poplabels" \
    --ancestor "$ANCESTOR" \
    -o "$prefix.input"

"$RELATE_ROOT/bin/Relate" --mode All \
    -m "$MUTATION_RATE" -N "$POP_SIZE" \
    --haps "$prefix.input.haps.gz" \
    --sample "$prefix.input.sample.gz" \
    --map "$MAP" --memory "${MEMORY_GB:-1}" \
    --annot "$prefix.input.annot" \
    --seed 1 -o "$prefix"
