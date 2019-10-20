#!/bin/bash
# Create environment file
conda env export --no-builds > ../environment.yml

# sed -i '/libgcc/d' ../environment.yml
# sed -i '/libstdcxx/d' ../environment.yml