#pragma once

#include "animation.h"
#include "program.h"
#include <memory>

class AnimatedProgram : public Program {
public:
    void SetColor(uint8_t red, uint8_t green, uint8_t blue)
    {
        red_ = red;
        green_ = green;
        blue_ = blue;
    }

    void SetBrightness(std::unique_ptr<AnimationSequence> sequence)
    {
        brightness_sequence_ = std::move(sequence);
    }

    void GetColor(uint32_t time_ms, uint8_t* red_out, uint8_t* green_out,
                  uint8_t* blue_out) override
    {
        *red_out = red_;
        *green_out = green_;
        *blue_out = blue_;
    }

    void GetBrightness(uint32_t time_ms, uint8_t* brightness_out) override
    {
        if (!brightness_sequence_) {
            *brightness_out = 255;
            return;
        }
        *brightness_out = brightness_sequence_->get(time_ms - time_base());
    }

    struct Segment {
        Animation animation[2];
    };

    void SetSegments(std::vector<Segment> segments) { segments_ = std::move(segments); }

    bool GetSegment(uint32_t time_ms, uint32_t segment_index, uint32_t* start_index,
                    uint32_t* end_index) override
    {
        if (segment_index >= segments_.size())
            return false;
        *start_index = segments_[segment_index].animation[0].get(time_ms - time_base());
        *end_index = segments_[segment_index].animation[1].get(time_ms - time_base());
        if (*start_index > *end_index) {
            uint32_t tmp = *start_index;
            *start_index = *end_index;
            *end_index = tmp;
        }
        return true;
    }

private:
    uint8_t red_ = 0;
    uint8_t green_ = 0;
    uint8_t blue_ = 0;

    std::unique_ptr<AnimationSequence> brightness_sequence_;
    std::vector<Segment> segments_;
};
