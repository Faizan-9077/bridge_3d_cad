
from crash_barriers import (
    create_crash_barrier_left,
    create_crash_barrier_right,
    place_crash_barrier
)


def create_median_barriers(
    length,
    barrier_width,
    barrier_height,
    barrier_base_width,
    deck_top_z,
    carriageway_center_y,
    median_gap
):
    """
    Creates median barriers using crash barrier geometry.
    """

    median_barriers = []

    offset = (median_gap / 2) + (barrier_base_width / 2)

    # LEFT median barrier
    left_barrier = create_crash_barrier_left(
        length=length,
        width=barrier_width,
        height=barrier_height,
        base_width=barrier_base_width
    )
    median_barriers.append(
        place_crash_barrier(
            left_barrier,
            x=0,
            y=carriageway_center_y - offset,
            z=deck_top_z
        )
    )

    # RIGHT median barrier
    right_barrier = create_crash_barrier_right(
        length=length,
        width=barrier_width,
        height=barrier_height,
        base_width=barrier_base_width
    )
    median_barriers.append(
        place_crash_barrier(
            right_barrier,
            x=0,
            y=carriageway_center_y + offset,
            z=deck_top_z
        )
    )

    return median_barriers
