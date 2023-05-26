-- Flex output script for importing natural=water polygons as nodes

-- Create a table for the filtered features
local water_reservoir_table = osm2pgsql.define_area_table("water_reservoir_areas",
    {
        { column = "osm_id", type = "bigint" },
        { column = "geom", type = "geometry" },
        { column = "natural", type = "text" }
    }
)

-- Filter function to select desired features
function filter_tags(tags, num_tags)
    -- Check if the feature has the desired tags
    if tags["natural"] == "water" then
        return 1 -- Include the feature
    else
        return 0 -- Exclude the feature
    end
end

-- Output function for filtered features
function output_area(tags, num_tags, area)
    -- Output the feature with its tags and geometry
    water_reservoir_table:add_row{
        osm_id = osm2pgsql.get_id(),
        geom = area,
        natural = tags["natural"]
    }
end

