#!/bin/bash
rm static/dashboard/config.js
touch static/dashboard/config.js

{
    echo "window.DASHBOARD_URL_MOVIE_APP = \"${DASHBOARD_URL}\""
} >> static/dashboard/config.js
