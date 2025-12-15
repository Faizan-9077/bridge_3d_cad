# validation.py

def validate_bridge_inputs(
    num_girders,
    girder_spacing,
    span_length,
    cross_bracing_spacing
):
    """
    Validates bridge input parameters based on design constraints.
    All dimensions are in millimetres.
    """

    # 1. Number of girders
    if num_girders <= 2 or num_girders >= 12:
        raise ValueError(
            "Number of girders must be greater than 2 and less than 12."
        )

    # 2. Girder spacing (1 m < spacing < 24 m)
    if girder_spacing <= 1000 or girder_spacing >= 24000:
        raise ValueError(
            "Girder spacing must be greater than 1 m and less than 24 m."
        )

    # 3. Span length (20 m < span < 45 m)
    if span_length <= 20000 or span_length >= 45000:
        raise ValueError(
            "Span length must be greater than 20 m and less than 45 m."
        )

    # 4. Cross bracing spacing (1 m < spacing < span length)
    if cross_bracing_spacing <= 1000:
        raise ValueError(
            "Cross bracing spacing must be greater than 1 m."
        )

    if cross_bracing_spacing >= span_length:
        raise ValueError(
            "Cross bracing spacing must be less than span length."
        )
