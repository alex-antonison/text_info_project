import pandas as pd
import json


class TextProcess(object):
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        self.state_map = pd.read_csv("reference/state_mapping.csv")

    def process_initial_json(self):
        with open(self.input_file) as json_file:
            data = json.load(json_file)

        df = pd.DataFrame.from_dict(data, orient='index').reset_index()

        df.rename(columns={'index':'report-key'}, inplace=True)

        return df

    def create_base_report(self, df):
        df.drop(columns=['public-notice', 'preliminary-report', 'fatality-alert', 'final-report'], inplace=True)

        for i in range(df.shape[0]):
            df.loc[i, 'location-processed'] = df.loc[i,'location'].split(",")[-1].replace(" ", "")

        df = df.merge(self.state_map, on='location-processed', how='left')

        df['state'] = df['state'].combine_first(df['location-processed'])

        ## There is a special case for report-key /data-reports/fatality-reports/2009/fatality-13-july-2-2009'
        ## where we need to hard code in the state since it was not properly put into the webpage
        ## you can see this here https://www.msha.gov/data-reports/fatality-reports/2009/fatality-13-july-2-2009
        df.loc[df['report-key'] == '/data-reports/fatality-reports/2009/fatality-13-july-2-2009', ('state')] = 'Pennsylvania'
              
        return df

    def extract_final_report_description(self, df):

        ## Get rid of the other columns
        df = df[~df['final-report'].isnull()]

        df = df[df['final-report'] != {}].loc[:,('report-key', 'final-report')].reset_index(drop=True)

        df['f-p-desc-of-accident'] = ''

        for item in range(df.shape[0]-1):
            keys = [x.lower() for x in df.loc[item, 'final-report'].keys()]
            
            if 'DESCRIPTION OF ACCIDENT'.lower() in keys:
                df.loc[item,'f-p-desc-of-accident'] = df.loc[item,'final-report']['DESCRIPTION OF ACCIDENT'].lower()
            elif 'DESCRIPTION OF THE ACCIDENT'.lower() in keys:
                df.loc[item,'f-p-desc-of-accident'] = df.loc[item,'final-report']['DESCRIPTION OF THE ACCIDENT'].lower()
            else:
                print(str(item) + " Does not have Description of Accident")

        return df

        ## TODO: Remove \xa0

        ## TODO: Remove punctuation



    def process_text(self):
        json_df = self.process_initial_json()

        report_df = self.extract_final_report_description(json_df)

        base_df = self.create_base_report(json_df)

        final_df = base_df.merge(report_df, on='report-key', how='left')

        print(report_df.head())

        print(final_df.head())

        final_df.to_csv(self.output_file, index=False)


def main():
    tp = TextProcess('data/report_info.json', 'data/base_fatality_reports.csv')

    tp.process_text()

if __name__ == "__main__":
    main()