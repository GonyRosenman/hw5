import pathlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
class QuestionnaireAnalysis:
    """
    Reads and analyzes data generated by the questionnaire experiment.
    Should be able to accept strings and pathlib.Path objects.
    """

    def __init__(self, data_fname: (pathlib.Path, str)):
        if isinstance(data_fname,str):
            self.data_fname = pathlib.Path(data_fname)
        else:
            self.data_fname = data_fname

    def read_data(self):
        """Reads the json data located in self.data_fname into memory, to
        the attribute self.data.
        """
        self.data = pd.read_json(self.data_fname)

    def show_age_distrib(self) -> (np.ndarray, np.ndarray):
        """Calculates and plots the age distribution of the participants.

    Returns
    -------
    hist : np.ndarray
      Number of people in a given bin
    bins : np.ndarray
      Bin edges
        """
        bin_edges = [*range(0,110,10)]
        self.data['age'].plot.hist(bins=bin_edges)
        plt.show()
        a,b = np.histogram(self.data['age'],bins=bin_edges)
        return a.astype(np.float),b

    def remove_rows_without_mail(self) -> pd.DataFrame:
        """Checks self.data for rows with invalid emails, and removes them.

    Returns
    -------
    df : pd.DataFrame
      A corrected DataFrame, i.e. the same table but with the erroneous rows removed and
      the (ordinal) index after a reset.
        """
        data_new = self.data.copy()
        for index,row in data_new.iterrows():
            if not row['email'].endswith('.com') and not 'chmotra3@live.c' in row['email']:
                data_new.drop(index,inplace=True)
            elif not '@' in row['email']:
                data_new.drop(index,inplace=True)
        return pd.DataFrame(data_new['email']).reset_index()

    def fill_na_with_mean(self) -> (pd.DataFrame, np.ndarray):
        """Finds, in the original DataFrame, the subjects that didn't answer
        all questions, and replaces that missing value with the mean of the
        other grades for that student.

    Returns
    -------
    df : pd.DataFrame
      The corrected DataFrame after insertion of the mean grade
    arr : np.ndarray
          Row indices of the students that their new grades were generated
        """
        students_with_gen_grades = []
        new_data = self.data.copy()
        qs = ['q1','q2','q3','q4','q5']
        cols = new_data.columns
        for index,row in new_data.iterrows():
            grades = row[qs]
            if grades.isna().any():
                students_with_gen_grades.append(index)
                actual_grades_mean = grades[~grades.isna()].mean()
                bad_q = [x for x,y in zip(qs,grades.isna().tolist()) if y]
                for q in bad_q:
                    new_data.iloc[index,cols.get_loc(q)] = actual_grades_mean
        return new_data,np.array(students_with_gen_grades)

    def score_subjects(self, maximal_nans_per_sub: int = 1) -> pd.DataFrame:
        """Calculates the average score of a subject and adds a new "score" column
        with it.

        If the subject has more than "maximal_nans_per_sub" NaN in his grades, the
        score should be NA. Otherwise, the score is simply the mean of the other grades.
        The datatype of score is UInt8, and the floating point raw numbers should be
        rounded down.

        Parameters
        ----------
        maximal_nans_per_sub : int, optional
            Number of allowed NaNs per subject before giving a NA score.

        Returns
        -------
        pd.DataFrame
            A new DF with a new column - "score".
        """
        new_data = self.data.copy()
        qs = ['q1', 'q2', 'q3', 'q4', 'q5']
        cols = new_data.columns
        score = []
        for index, row in new_data.iterrows():
            grades = row[qs]
            if grades.isna().any():
                if grades.isna().sum() >= maximal_nans_per_sub:
                    score.append('NA')
                else:
                    actual_grades_mean = np.floor(grades[~grades.isna()].mean()).astype(np.uint8)
                    score.append(actual_grades_mean)
            else:
                score.append(np.floor(grades.mean()).astype(np.uint8))
        new_data['score'] = score
        return new_data
