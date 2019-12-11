import pandas as pd

class TextProcess(object):
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        ## This is necessary in order to clean up the 
        ## state mappings as they are not standard
        ## which makes it difficult to visualize
        self.state_map = pd.read_csv("reference/state_mapping.csv")

    def process_initial_json(self):
        """Read in json file and turn into df
        
        Returns:
            df -- The scraped reports returned as a json file
        """
        df = (pd.read_json(self.input_file)
                .transpose()
                .reset_index()
                .rename(columns={"index":"report-key"}))

        return df

    def create_base_report(self, df):
        """Create the base information dataframe

        This dataframe will include all of the fields that contain 
        standard information that does not require further porcessing.
        
        Arguments:
            df {dataframe} -- The processed dataframe produced by the process_initial_json method
        
        Returns:
            dataframe -- returns a processed dataframe with the base columns
        """
        ## Dropping the free text columns
        df.drop(columns=['public-notice', 'preliminary-report', 'fatality-alert', 'final-report'], inplace=True)

        ## Often times additional information
        ## was provided with the location.
        ## Since city was not always provided,
        ## we decided to just get the state which typically
        ## came after the last comma
        for i in range(df.shape[0]):
            df.loc[i, 'location-processed'] = df.loc[i,'location'].split(",")[-1].replace(" ", "")

        df = df.merge(self.state_map, on='location-processed', how='left')

        ## Create the final state column to be used in data visuals
        df['state'] = df['state'].combine_first(df['location-processed'])

        ## There is a special case for report-key /data-reports/fatality-reports/2009/fatality-13-july-2-2009'
        ## where we need to hard code in the state since it was not properly put into the webpage
        ## you can see this here https://www.msha.gov/data-reports/fatality-reports/2009/fatality-13-july-2-2009
        df.loc[df['report-key'] == '/data-reports/fatality-reports/2009/fatality-13-july-2-2009', ('state')] = 'Pennsylvania'
              
        return df

    def keep_only_letters(self, row_string):
        '''
        This method removes everything except spaces and letters to help
        facilitate performing topic analysis.

        Arguments:
            row_string {string} -- The pandas column we are wanting to strip

        Returns:
            string -- a cleaned up string 
        '''
        whitelist = set('abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        return ''.join(filter(whitelist.__contains__, row_string))

    def extract_final_report_description(self, df):
        """Produce a dataframe for analyzing final report

        This method pulls out the description of the accident from the 
        final report, leaves only letters and spaces, and returns a dataframe
        of just the report-key and the column to be added to the final
        dataframe.
        
        Arguments:
            df {dataframe} -- The processed dataframe produced by the process_initial_json method
        
        Returns:
            dataframe -- A dataframe 
        """
        ## Git rid of instances where a fatality report
        ## does not have a final report
        df = df[~df['final-report'].isnull()]

        ## There are some instances where a report
        ## has a final report, but it has a non-standard method
        ## of labeling it and it was missed in the scraping.
        df = df[df['final-report'] != {}].loc[:,('report-key', 'final-report')].reset_index(drop=True)

        ## Initialize the column
        df['f-p-desc-of-accident_pre'] = ''

        ## Loop through and extract the description for each key based on the
        ## available section
        for item in range(len(df)):

            keys = df.loc[item, 'final-report'].keys()

            if 'description of accident' in keys:
                df.loc[item,'f-p-desc-of-accident_pre'] = df.loc[item,'final-report']['description of accident']
            elif 'description of the accident' in keys:
                df.loc[item,'f-p-desc-of-accident_pre'] = df.loc[item,'final-report']['description of the accident']

        ## cleans up the text
        df['f-p-desc-of-accident'] = df.apply(lambda x : self.keep_only_letters(x['f-p-desc-of-accident_pre']), axis = 1)

        ## To analyze output, saving this to csv to 
        ## do a comparison of what it looked like before
        ## and after cleanup
        df = df.loc[:,('report-key', 'f-p-desc-of-accident_pre', 'f-p-desc-of-accident')]

        ## This was included for comparative purposes
        df.to_csv("data/final_report_pre_and_post_processing.csv", sep="|", index=False)

        ## For final output, only want to include the actual column
        df = df.loc[:,('report-key', 'f-p-desc-of-accident')]

        return df


    def process_text(self):
        """Primary method for processing text

        This method is used create the two different dataframes
        and output a final combined dataframe for further analysis.
        """
        json_df = self.process_initial_json()

        report_df = self.extract_final_report_description(json_df)

        base_df = self.create_base_report(json_df)

        combined_df = base_df.merge(report_df, on='report-key', how='left')

        combined_df.to_csv(self.output_file, index=False, sep="|")


def main():
    tp = TextProcess('data/report_info.json', 'data/base_fatality_reports.csv')

    tp.process_text()

if __name__ == "__main__":
    main()