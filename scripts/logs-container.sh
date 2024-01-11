#!/bin/bash

OUTPUT=$(sudo docker container ls | grep movie | cut -c1-12)
sudo docker logs -f "${OUTPUT}"