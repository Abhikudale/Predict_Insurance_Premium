import os
from insurance.entity.insurance_predictor import InsuranceData, InsurancePredictor
from insurance.pipeline.pipeline import Pipeline
from insurance.exception import InsuranceException
from insurance.logger import logging
from insurance.config.configuration import Configuration
from insurance.component.data_transformation import DataTransformation
import os

from insurance.util.util import load_object
def main():
    try:
        #data_validation_config=Configuration().get_data_transformation_config()
        #print(data_validation_config)
        #Start:-Execute below code to create model
        config_path = os.path.join("config","config.yaml")
        pipeline = Pipeline(Configuration(config_file_path=config_path))
        pipeline.start()
        logging.info("main function execution completed.")
        #End:-Execute below code to create model
        #data_validation_config = Configuration().get_data_transformation_config()
        #print(data_validation_config)
        #schema_file_path=r"D:\Project\machine_learning_project\config\schema.yaml"
        #file_path=r"D:\Project\machine_learning_project\insurance\artifact\data_ingestion\2022-06-27-19-13-17\ingested_data\train\insurance.csv"

        # df= DataTransformation.load_data(file_path=file_path,schema_file_path=schema_file_path)
        # print(df.columns)
        # print(df.dtypes)

        # insurance_data = InsuranceData(age=56,
        #                            sex="male",
        #                            bmi=32.4,
        #                            children=4,
        #                            smoker="no",
        #                            region="southwest"
        #                            )
        # insurance_df = insurance_data.get_insurance_input_data_frame()
        # model = load_object(file_path=r"C:\MLProjects\Predict_Insurance_Premium\saved_models\20220806135312\model.pkl")
        # expenses = model.predict(insurance_df)
        # print(expenses)

    except Exception as e:
        logging.error(f"{e}")
        print(e)

if __name__=="__main__":
    main()
