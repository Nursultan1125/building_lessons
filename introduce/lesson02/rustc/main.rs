use std::collections::HashMap;
use std::fs::File;
use std::io::{self, BufRead, BufReader};

#[derive(Debug)]
struct Point {
    x: f64,
    y: f64,
    z: f64,
}

#[derive(Debug)]
struct Line {
    start: Point,
    end: Point,
}

#[derive(Debug)]
struct E3DFace {
    points: [Point; 4],
}

struct DXFParser {
    point_map: HashMap<String, f64>,
}

impl DXFParser {
    fn new() -> Self {
        Self {
            point_map: HashMap::new(),
        }
    }

    fn parse_point(&self, point_data: &HashMap<String, f64>) -> Point {
        Point {
            x: *point_data.get("10").unwrap_or(&0.0),
            y: *point_data.get("20").unwrap_or(&0.0),
            z: *point_data.get("30").unwrap_or(&0.0),
        }
    }

    fn parse_line(&self, line_data: &HashMap<String, f64>) -> Line {
        Line {
            start: Point {
                x: *line_data.get("10").unwrap_or(&0.0),
                y: *line_data.get("20").unwrap_or(&0.0),
                z: *line_data.get("30").unwrap_or(&0.0),
            },
            end: Point {
                x: *line_data.get("11").unwrap_or(&0.0),
                y: *line_data.get("21").unwrap_or(&0.0),
                z: *line_data.get("31").unwrap_or(&0.0),
            },
        }
    }

    fn parse_3dface(&self, face_data: &HashMap<String, f64>) -> E3DFace {
        E3DFace {
            points: [
                Point {
                    x: *face_data.get("10").unwrap_or(&0.0),
                    y: *face_data.get("20").unwrap_or(&0.0),
                    z: *face_data.get("30").unwrap_or(&0.0),
                },
                Point {
                    x: *face_data.get("11").unwrap_or(&0.0),
                    y: *face_data.get("21").unwrap_or(&0.0),
                    z: *face_data.get("31").unwrap_or(&0.0),
                },
                Point {
                    x: *face_data.get("12").unwrap_or(&0.0),
                    y: *face_data.get("22").unwrap_or(&0.0),
                    z: *face_data.get("32").unwrap_or(&0.0),
                },
                Point {
                    x: *face_data.get("13").unwrap_or(&0.0),
                    y: *face_data.get("23").unwrap_or(&0.0),
                    z: *face_data.get("33").unwrap_or(&0.0),
                },
            ],
        }
    }

    fn parse(&mut self, filepath: &str) -> io::Result<()> {
        let file = File::open(filepath)?;
        let reader = BufReader::new(file);
        let mut lines = reader.lines().peekable();

        let mut current_entity = String::new();
        let mut current_data = HashMap::new();

        while let Some(line) = lines.next() {
            let line = line?;
            if let Some(code) = line.trim().parse::<i32>().ok() {
                if let Some(value) = lines.next() {
                    let value = value?;
                    if code == 0 {
                        if current_entity == "POINT" {
                            let point = self.parse_point(&current_data);
                            println!("Parsed POINT: {:?}", point);
                        } else if current_entity == "LINE" {
                            let line = self.parse_line(&current_data);
                            println!("Parsed LINE: {:?}", line);
                        } else if current_entity == "3DFACE" {
                            let face = self.parse_3dface(&current_data);
                            println!("Parsed 3DFACE: {:?}", face);
                        }
                        current_entity = value;
                        current_data.clear();
                    } else {
                        current_data.insert(code.to_string(), value.parse().unwrap_or(0.0));
                    }
                }
            }
        }
        Ok(())
    }
}

fn main() -> io::Result<()> {
    let mut parser = DXFParser::new();
    parser.parse("data/test.dxf")?;
    Ok(())
}
