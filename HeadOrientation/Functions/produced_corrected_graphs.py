# from HeadOrientation.Parsing.parse_ear_data import parse_multiple_subjects
from Data.Functions.parse_data import parse_multiple_subjects
from HeadOrientation.Visualisation.view_head_orientation import view_orientation_all_subjects
import MatlabAHRSPackage


def produce_corrected_graphs(subjectStart, subjectEnd):
    """ Combine sequence of steps to produce head rotation-corrected data for desired subjects """
    # parse the data into correct NED format
    parse_multiple_subjects(subjectStart, subjectEnd, activityTypes=["Walk"])
    # Perform the AHRS orientation algorithm to find head orientation rotation matrices
    MatlabAHRSPackage.calculate_head_orientation_multiple(subjectStart, subjectEnd, activityTypes=["Walk"])
    # Apply rotation matrices to produce rotation-corrected graphs
    view_orientation_all_subjects(subjectStart, subjectEnd, ["Walk"], filter=False)


def main():
    produce_corrected_graphs(1, 2)


if __name__ == "__main__":
    main()
