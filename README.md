# Prediction of Learners’ Performance based on Link Prediction in a Knowledge Graph

This project contains the code developed for the experiments on the "Prediction of Learners’ Performance based on 
Link Prediction in a Knowledge Graph".
Due to confidentiality constraints, we are not allowed to release data concerning the OntoSIDES Knowledge Graph, 
therefore the present project only includes scripts and data to reproduce the experiments on the ASSISTments dataset and 
Knowledge Graph.

## Project content
The structure of the project is as follows:
* **./configs/** contains the python configuration file with the proper paths and customized functions used for the 
experiments on the ASSISTments dataset;
* **./data/** contains the training and test sets used for the experiments on the ASSISTments 
(in the sub-directory **./data/datasets/assistments/**); as well as the Knowledge Graph built from such data 
(in the sub-directory **./data/graphs/assistments/**); and the empty directory **./data/gembs/assistments/** where the 
computed GEs for each model should be placed (See "Computing Graph Embeddings").
* **./results/assistments/** contains the results obtained through our experiments.


## Reproducing the experiments
To execute the scripts included in this project you will need a Python environment containing the packages list in 
the file **requirements.txt**.
Once your Python environment is ready, you can reproduce the experiments using the datasets provided in 
**./data/datasets/assistments/** and the Knowledge Graph created starting from these data, which is located in 
**./data/graphs/assistments/**.
To reproduce the results of the experiments, you first to run the script **preprocess.py** which, using the 
configuration provided in **configs/assistments.py**, will create the proper directory structure and the files necessary
for the computation of the embeddings and the later evaluation of the results.

More precisely, the script will create the following files:
* **./graphs/assistments/graph.txt**: the file containing the list of the triples of the Knowledge Graph in CSV format,
to be used for the computation of the embeddings (see section "Computing Knowledge Graph Embeddings" below);
* **./graphs/assistments/triples_possible.txt**: the file containing the list of all the possible triples whose score 
we want to predict;
* **./graphs/assistments/triples_possible.txt**: the file containing the list of all the real triples 
(among the possible ones), which represents the ground truth for out evaluation.

Moreover, the subdirectory **./gembs/assistments/TransE_l2/config0** will be created to store the Graph Embeddings to 
be used for link prediction (see section "Computing Knowledge Graph Embeddings" below).

After the preprocessing, the KGEs need to be computed as illustrated in the following section
("Computing Knowledge Graph Embeddings").
Once the KGEs are computed and stored in the correct directory (**./gembs/assistments/TransE_l2/config0**), the script 
**map_transform_input.py** can be used to create the input files for the Link Prediction model.
The script simply maps the triples in the file **./graphs/assistments/triples_possible.txt** to the numerical 
IDs of the graph elements used by the KGEs.
The three files created by the script, **heads.list**, **tails.list** and **rels.list**, are saved in 
**./gembs/assistments/TransE_l2/config0** and contain respectively the IDs of the heads, tails and relations of the
triples in **./graphs/assistments/triples_possible.txt**.
These files can be used to compute the Link Prediction scores as explained in section "Computing Link Prediction Scores".

Finally, the script **eval_output.py** can be used to evaluate the results of the Link Prediction, from the output file 
**./gembs/assistments/TransE_l2/config0/results.tsv**.
The final metrics for the task on prediction of students' outcomes will be saved in the directory **results/assistments**.


## Computing Knowledge Graph Embeddings
Due to the restrictions on the file size imposed by GitHub is not possible for us to upload the computed GEs along 
with the present project. Therefore, to reproduce our results you will need to compute the GEs 
of the graph located in **./data/graphs/assistments/** and place them in the correct sub-directory of 
**./data/gembs/assistments/** (**./data/gembs/assistments/TransE_l2/config0/** if you use the same KGE model).

### TransE_l2
To compute KGEs, we made use of the AWS DGL-KGE library
(https://aws-dglke.readthedocs.io/en/latest/index.html). The commands used for the GEs computation for each model are 
listed hereafter.

```
DGLBACKEND=pytorch dglke_train --model_name TransE_l2 --data_path ./ --dataset assistments --format raw_udd_hrt --data_files graph.txt --delimiter ',' --batch_size 1000 --log_interval 1000 \
--neg_sample_size 200 --regularization_coef=1e-9 --hidden_dim 100 --gamma 19.9 \
--lr 0.25 --batch_size_eval 16 --gpu 0 1 2 3 --async_update --max_step 100000 --force_sync_interval 1000
```

The input file **graph.txt** (located in **./data/graphs/assistments/**) contains the list of the triples in the graph, 
in CSV format.
The output files containing the KGEs of entities and relations are saved in the sub-directories
**./ckpts/TransE_l2_assistments_0/** of your AWS DGL-KGE library location.
These files need to be moved in the corresponding directories **./datasets/gembs/assistments/TransE_l2/config0** 
together with the two mapping files **entities.tsv** and **relations.tsv** which associate a numerical ID to each URI in
the KG.

## Computing Link Prediction Scores

To compute the Link Prediction scores, we need to copy the input files generated at the previous step in the directory 
containing the previously computed KGEs under the AWS DGL-KGE library location.
The commands used for the computation of the scores are the following:

```
DS_PATH='ckpts/TransE_l2_assistments_0'
MODE='triplet_wise'
K=125528
DGLBACKEND=pytorch dglke_predict --model_path $DS_PATH/ --format 'h_r_t' \
--data_files $DS_PATH/heads.list $DS_PATH/rels.list $DS_PATH/tails.list --topK $K --exec_mode $MODE \
--output $DS_PATH/result.tsv
```
The file **result.tsv** contains the scores for each triple in the file **./graphs/assistments/triples_possible.txt**.
This file must be now moved in the directory **./gembs/assistments/TransE_l2/config0/** and can be used to evaluate the
results of the Link Prediction through the script **eval_output.py**.


## Repeating the experiments on other Knowledge Graphs
The present approach and code can be used to predict students outcomes to questions in other KGs.
To do so, a new configuration file must be created in the **./configs/** directory, containing the path and the functions 
to use for this new KG.
It is important to highlight that such KG must contain the complete description of the answers to be used as 
"training set", including the results of such answers (correct or incorrect); while it must contain only the answer node
properly linked to the corresponding student and question nodes, without the result of the answer, for the "test set".
Once the KG is ready and the configuration file properly created, the results can be obtained through process 
illustrated in section "Reproducing the experiments".
Please note that experiments on the same Knowledge Graph with different KGE models or different settings cn be simply 
perfomed by changing the configuration file and running the scripts again.

