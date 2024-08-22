#!/bin/bash
env > /home/ubuntu/cron_env.log
source /home/ubuntu/miniconda3/etc/profile.d/conda.sh
conda activate geoglows
/home/ubuntu/miniconda3/envs/geoglows/bin/python /home/ubuntu/inamhi-geoglows/taskfiles/fireforest/daily_pacum.py
/home/ubuntu/miniconda3/envs/geoglows/bin/python /home/ubuntu/inamhi-geoglows/taskfiles/fireforest/soil_moisture.py
/home/ubuntu/miniconda3/envs/geoglows/bin/python /home/ubuntu/inamhi-geoglows/taskfiles/fireforest/report.py
/home/ubuntu/miniconda3/envs/geoglows/bin/python /home/ubuntu/inamhi-geoglows/taskfiles/sgr/main.py