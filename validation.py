# validation.py

def validate_bridge_inputs(
    num_girders,
    girder_spacing,
    span_length,
    cross_bracing_spacing,
    deck_thickness=None,
    footpath_config=None,
    footpath_width=None
):
    """
    Validates bridge input parameters based on design constraints
    and cross-section guidelines (as per given figure).
    All dimensions are in millimetres.
    """

    # -------------------------------------------------
    # 1. Number of girders
    # -------------------------------------------------
    if num_girders <= 2 or num_girders >= 12:
        raise ValueError(
            "Number of girders must be greater than 2 and less than 12."
        )

    # -------------------------------------------------
    # 2. Girder spacing (1 m < spacing < 24 m)
    # -------------------------------------------------
    if girder_spacing <= 1000 or girder_spacing >= 24000:
        raise ValueError(
            "Girder spacing must be greater than 1 m and less than 24 m."
        )

    # -------------------------------------------------
    # 3. Span length (20 m < span < 45 m)
    # -------------------------------------------------
    if span_length <= 20000 or span_length >= 45000:
        raise ValueError(
            "Span length must be greater than 20 m and less than 45 m."
        )

    # -------------------------------------------------
    # 4. Cross bracing spacing (1 m < spacing < span)
    # -------------------------------------------------
    if cross_bracing_spacing <= 1000:
        raise ValueError(
            "Cross bracing spacing must be greater than 1 m."
        )

    if cross_bracing_spacing >= span_length:
        raise ValueError(
            "Cross bracing spacing must be less than span length."
        )

    # -------------------------------------------------
    # 5. Carriageway width check (from figure)
    # 4.25 m < width < 24 m
    # -------------------------------------------------
    carriageway_width = (num_girders - 1) * girder_spacing

    if carriageway_width <= 4250 or carriageway_width >= 24000:
        raise ValueError(
            f"Carriageway width {carriageway_width} mm is invalid. "
            "Allowed range: 4250 mm < width < 24000 mm."
        )

    # -------------------------------------------------
    # 6. Deck thickness check (from figure)
    # 100 mm < thickness < 500 mm
    # -------------------------------------------------
    if deck_thickness is not None:
        if deck_thickness <= 100 or deck_thickness >= 500:
            raise ValueError(
                f"Deck thickness {deck_thickness} mm is invalid. "
                "Allowed range: 100 mm < thickness < 500 mm."
            )

    # -------------------------------------------------
    # 7. Footpath width check (from figure)
    # 0 < width < 10 m (only if footpath exists)
    # -------------------------------------------------
    # if footpath_config is not None and footpath_config != "NONE":
    #     if footpath_width is None:
    #         raise ValueError(
    #             "Footpath width must be provided when footpath is present."
    #         )

    #     if footpath_width <= 0 or footpath_width >= 10000:
    #         raise ValueError(
    #             f"Footpath width {footpath_width} mm is invalid. "
    #             "Allowed range: 0 < width < 10000 mm."
    #         )
