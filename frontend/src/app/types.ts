export type MarkdownFiles = Record<string, string>;

export type ConditionAlertFailure = {
    pred: (state: HomepageState) => boolean;
    error_msg: string;
};

export interface HomepageState {
    modelURL: string;
    datasetURL: string;
    modelAPIKey: string;
    datasetAPIKey: string;
    isModelURLValid: boolean;
    isDatasetURLValid: boolean;
    activeStep: number;
    selectedItem: string;
    metricChips: { id: string; label: string; selected: boolean }[];
    metricsHelperText: string;
    selectedModelType: string;
    error: boolean;
    errorMessage: { header: string; text: string };
  }
