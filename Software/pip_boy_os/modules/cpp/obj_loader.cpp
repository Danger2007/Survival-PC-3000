#include "obj_loader.hpp"
#include "math.hpp"
#include <fstream>
#include <iostream>
#include <iterator>
#include <sstream>

Obj::Obj(const std::string &file_path)
{

    parse_file(file_path);
    Point3D center = {0, 0, 0};
    Point3D min = {1e30, 1e30, 1e30};
    Point3D max = {-1e30, -1e30, -1e30};
    for (auto &i : v)
    {
        center.x += i.x;
        center.y += i.y;
        center.z += i.z;
    }
    center.x /= v.size();
    center.y /= v.size();
    center.z /= v.size();
    for (auto &i : v)
    {
        i.x -= center.x;
        i.y -= center.y;
        i.z -= center.z;
    }



};

void Obj::parse_file(const std::string &file_path)
{
    std::ifstream file(file_path);
    std::string current_line;
    if (file.is_open())
    {
        while (getline(file, current_line))
        {
            if (current_line.empty())
                continue;
            if (current_line.rfind("v ", 0) == 0)
            {
                // parce vertices
                float x, y, z;
                std::istringstream(current_line.substr(2, std::string::npos)) >> x >> z >> y;
                v.push_back({x, -y, z});
            }
            else if (current_line.rfind("vn ", 0) == 0)
            {
                // normal, skip for now
            }
            else if (current_line.rfind("vt ", 0) == 0)
            {
                // texture, skip
            }
            else if (current_line.rfind("f ", 0) == 0)
            {
                std::string part;
                unsigned int v1, v2, v3;
                std::istringstream ss(current_line.substr(2)); // skip "f "

                // Read first vertex
                ss >> part;
                v1 = std::stoi(part.substr(0, part.find('/')));

                // Second vertex
                ss >> part;
                v2 = std::stoi(part.substr(0, part.find('/')));

                // Third vertex
                ss >> part;
                v3 = std::stoi(part.substr(0, part.find('/')));

                f.push_back({v1 - 1, v2 - 1, v3 - 1}); // 0-based indexing
            }
            else if (current_line.rfind("o ", 0) == 0)
            {
                // parse object name
                name = current_line.substr(2, std::string::npos);
            }
        }
        file.close();
    }
    else
    {
        std::cerr << "Unable to open file " << file_path << std::endl;
    }
};