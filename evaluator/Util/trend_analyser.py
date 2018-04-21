import talib

from evaluator.Util.abstract_util import AbstractUtil
from evaluator.Util.analysis_util import AnalysisUtil


class TrendAnalyser(AbstractUtil):

    # trend < 0 --> Down trend
    # trend > 0 --> Up trend
    @staticmethod
    def get_trend(data_frame, averages_to_use):
        trend = 0
        inc = round(1 / len(averages_to_use), 2)
        averages = []

        # Get averages
        for average_to_use in averages_to_use:
            averages.append(data_frame.tail(average_to_use).values.mean())

        for a in range(0, len(averages) - 1):
            if averages[a] - averages[a + 1] > 0:
                trend -= inc
            else:
                trend += inc

        return trend

    # < 0 --> Current average bellow other one (computed using time_period)
    # > 0 --> Current average above other one (computed using time_period)
    @staticmethod
    def get_moving_average_analysis(data_frame, time_period):

        current_unit_moving_average = talib.MA(data_frame, timeperiod=2, matype=0)
        time_period_unit_moving_average = talib.MA(data_frame, timeperiod=time_period, matype=0)

        # compute difference between 1 unit values and others ( >0 means currently up the other one)
        values_difference = (current_unit_moving_average - time_period_unit_moving_average).dropna()

        # indexe where current_unit_moving_average crosses time_period_unit_moving_average
        mean_crossing_indexes = AnalysisUtil.get_sign_change_indexes(values_difference)

        multiplier = 1
        if not values_difference.iloc[-1] > 0:
            multiplier = -1

        # check enough data in the frame (at least 2) => did not just crossed the other curve
        if len(mean_crossing_indexes) > 0 and mean_crossing_indexes[-1] < values_difference.count()-2:
            current_divergence_data = values_difference[mean_crossing_indexes[-1]+1:]
            normalized_data = AnalysisUtil.normalize_data_frame(current_divergence_data)
            current_value = (normalized_data.iloc[-1]+1)/2
            # check <= values_difference.count()-1if current value is max/min
            if current_value == 0 or current_value == 1:
                chances_to_be_max = AnalysisUtil.get_estimation_of_move_state_relatively_to_previous_moves_length(
                                                                                                mean_crossing_indexes)
                return multiplier*current_value*chances_to_be_max
            # other case: maxima already reached => return distance to max
            else:
                return multiplier*current_value

        # just crossed the average => neutral
        return 0
