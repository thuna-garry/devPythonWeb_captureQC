module.exports = function(grunt) {

	grunt.initConfig({

		// Import package manifest
		pkg: grunt.file.readJSON("package.json"),

		// Banner definitions
		meta: {
			banner: '/*\n' + 
			' * <%= pkg.title || pkg.name %> - v<%= pkg.version %>\n' +
			' * <%= pkg.description %>\n' +
      		' * <%= pkg.homepage %>\n' +
      		' *\n' +
      		' * Copyright (c) <%= grunt.template.today("yyyy") %> <%= pkg.author %>\n' +
      		' * Licensed under the <%= pkg.license %> license.\n' +
      		' */\n\n'
		},

		// Concat definitions
		concat: {
			all: {
				src: ["src/jquery.mobile.toast.js"],
				dest: "dist/jquery.mobile.toast.js"
			},
			options: {
				banner: "<%= meta.banner %>"
			}
		},

		// Lint definitions
		jshint: {
			files: ["src/jquery.mobile.toast.js"],
			options: {
				jshintrc: ".jshintrc"
			}
		},

		// Check code style
		jscs: {
		    files: ["src/jquery.mobile.toast.js"],
		    options: {
		        config: ".jscsrc"
		    }
		},

		// Minify definitions
		uglify: {
			all: {
				src: ["dist/jquery.mobile.toast.js"],
				dest: "dist/jquery.mobile.toast.min.js"
			},
			options: {
				banner: "<%= meta.banner %>"
			}
		},

		clean: ["dist"],

		jasmine: {
			all: {
				src: "src/jquery.mobile.toast.js",
				options: {
					vendor: [
						"http://code.jquery.com/jquery-1.9.1.min.js",
						"http://code.jquery.com/mobile/1.3.2/jquery.mobile-1.3.2.min.js"
					],
					specs: "test/spec/{,*/}*.js"
				}
			}
		},

		// Generate documentation
		yuidoc: {
			compile: {
				name:        "<%= pkg.name %>",
				description: "<%= pkg.description %>",
				version:     "<%= pkg.version %>",
				url:         "<%= pkg.homepage %>",
				options: {
					paths:    "src",
					outdir:   "docs"
				}
			}
		},

		watch: {
			scripts: {
				files: ["src/*.js"],
				tasks: ["jshint", "clean","concat", "uglify", "yuidoc"]
			}
		}

	});

	grunt.loadNpmTasks("grunt-contrib-concat");
	grunt.loadNpmTasks("grunt-contrib-jshint");
	grunt.loadNpmTasks("grunt-contrib-uglify");
	grunt.loadNpmTasks("grunt-contrib-clean");
	grunt.loadNpmTasks("grunt-contrib-yuidoc");
	grunt.loadNpmTasks("grunt-contrib-watch");
	grunt.loadNpmTasks("grunt-contrib-jasmine");
	grunt.loadNpmTasks("grunt-jscs");

	grunt.registerTask("default", ["jshint", "jscs", "clean","concat", "uglify", "jasmine", "yuidoc"]);
	grunt.registerTask("test", ["jasmine"]);

};
