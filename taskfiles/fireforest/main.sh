#!/bin/bash
source /home/ubuntu/miniconda3/etc/profile.d/conda.sh
conda activate geoglows
python /home/ubuntu/inamhi-geoglows/taskfiles/fireforest/daily_pacum.py
python /home/ubuntu/inamhi-geoglows/taskfiles/fireforest/soil_moisture.py
python /home/ubuntu/inamhi-geoglows/taskfiles/fireforest/report.py
python /home/ubuntu/inamhi-geoglows/taskfiles/sgr/main.py
python /home/ubuntu/inamhi-geoglows/taskfiles/celec/main_paute.py
python /home/ubuntu/inamhi-geoglows/taskfiles/celec/hydropower_report.py
