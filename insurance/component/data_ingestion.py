
from this import d
from sklearn.model_selection import StratifiedShuffleSplit
from six.moves import urllib
from insurance.entity.config_entity import DataIngestionConfig
from insurance.exception import InsuranceException
from insurance.entity.artifact_entity import DataIngestionArtifact
from insurance.logger import logging
import pandas as pd
import numpy as np
import os, sys
import tarfile
import shutil

class DataIngestion:
    def __init__(self, data_ingestion_config:DataIngestionConfig):
        try:
            logging.info(f"{'='*20}Data Ingestion log started.{'='*20}")
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise InsuranceException(e,sys) from e

    def download_insurance_data(self,) -> str:
        try:
            #extract remote url to download dataset
            
            download_url = self.data_ingestion_config.dataset_download_url
            
            #folder location to download file
            tgz_download_dir = self.data_ingestion_config.tgz_download_dir
            
            ROOT_DIR = os.getcwd()
            download_url = os.path.join(ROOT_DIR,download_url,"insurance.csv")
            
            os.makedirs(tgz_download_dir,exist_ok=True)

            insurance_file_name = os.path.basename(download_url)

            tgz_file_path = os.path.join(tgz_download_dir,insurance_file_name)
            logging.info(f"Downloading file from :[{download_url}] in to :[{tgz_file_path}]")
            
            shutil.copyfile(download_url,tgz_file_path)
            #urllib.request.urlretrieve(download_url,tgz_file_path)
            logging.info(f"File:[{tgz_file_path}] has been downloaded successfully")

            return tgz_file_path

        except Exception as e:
            raise InsuranceException(e,sys) from e

    def extract_tgz_file(self,tgz_file_path:str):
        try:
            raw_data_dir = self.data_ingestion_config.raw_data_dir

            if os.path.exists(raw_data_dir):
                os.remove(raw_data_dir)

            os.makedirs(raw_data_dir,exist_ok=True)

            logging.info("Extracting tgz file: [{tgz_file_path}] in to dir: [{raw_data_dir}]")
            #with tarfile.open(tgz_file_path) as insurance_tgz_file_obj:
                #insurance_tgz_file_obj.extractall(path=raw_data_dir)
            shutil.copy(tgz_file_path,raw_data_dir)
            logging.info(f"Extraction completed")
            
        
        except Exception as e:
            raise InsuranceException(e,sys) from e

    def split_data_as_train_test(self) -> DataIngestionArtifact:
        try:
            raw_data_dir = self.data_ingestion_config.raw_data_dir
            
            file_name = os.listdir(raw_data_dir)[0]
            
            insurance_file_path = os.path.join(raw_data_dir,file_name)
            
            logging.info(f"Reading csv file:[{insurance_file_path}]")

            insurance_data_frame = pd.read_csv(insurance_file_path)
            insurance_data_frame = insurance_data_frame.head(10000)
            #Dropping Sex column as output column expenses is not dependent on Sex column
            insurance_data_frame.drop(columns="sex", axis=1, inplace=True)

            insurance_data_frame["age_cat"] = pd.cut(
                insurance_data_frame["age"],
                bins=[0, 20, 30, 40, 50, 60, np.inf],
                labels= [1,2,3,4,5,6]
            )

            logging.info(f"Splitting data in to Train and Test dataset")

            strat_train_set = None

            strat_test_set = None

            split = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)

            for train_index, test_index in split.split(insurance_data_frame, insurance_data_frame["age_cat"]):
                strat_train_set = insurance_data_frame.loc[train_index].drop(["age_cat"], axis=1)
                strat_test_set = insurance_data_frame.loc[test_index].drop(["age_cat"], axis=1)
            
            train_file_path = os.path.join(self.data_ingestion_config.ingested_train_dir,file_name)

            test_file_path = os.path.join(self.data_ingestion_config.ingested_test_dir,file_name)

            if strat_train_set is not None:
                os.makedirs(self.data_ingestion_config.ingested_train_dir,exist_ok=True)
                logging.info(f"Exporting training dataset in to file:[{train_file_path}]")
                strat_train_set.to_csv(train_file_path,index=False)
                
            if strat_test_set is not None:
                os.makedirs(self.data_ingestion_config.ingested_test_dir,exist_ok=True)
                logging.info(f"Exporting testing dataset in to file:[{test_file_path}]")
                strat_test_set.to_csv(test_file_path,index=False)
                
            data_ingestion_artifact = DataIngestionArtifact(train_file_path = train_file_path,
                                test_file_path=test_file_path,
                                is_ingested=True,
                                message=f"Data ingestion completed successfully."
                                )
            logging.info(f"Data ingestion Artifact:[{data_ingestion_artifact}]")
            return data_ingestion_artifact

        except Exception as e:
            raise InsuranceException(e,sys) from e

    def initiate_data_ingestion(self) ->DataIngestionArtifact:
        try:
            tgz_file_path = self.download_insurance_data()

            self.extract_tgz_file(tgz_file_path=tgz_file_path)

            return self.split_data_as_train_test()

        except Exception as e:
            raise InsuranceException(e,sys) from e

    def __del__(self):
        logging.info(f"{'='*20}Data Ingestion log completed.{'='*20}\n\n")
