# TODO

- [X] Remove extraneous operations from natural API.
    Is this really necessary? From what I can see, `op_get_bits()` can replace
    `op_get_byte()` but getting bytes requires the validation of a different
    contract than getting bits (logical group of 8 bits). Since that is a very
    common contract to expose to higher level layers, I hesitate to lift it.
    Furthermore, it would be interesting to note what other "pure" operations
    there are. For instance, Rust's bytemuck has many operations not currently
    supported by Tidbytes but this is largely due to the fact that Tidbytes
    takes a strong stance on separating high from low level API surfaces. As
    such it may be more appropriate for the lower level API to provide some
    helper operations but not codecs (the bridges between high and low level).

- [ ] Fully test idiomatic operations

- [ ] Go back through and fix typos, documentation, and formatting

- [ ] Create exception heirarchy for exact errors. Analyze codebase. Is this
    something that is useful? I think so since IEEE754 defines exceptions.

> What would it take to consider this project done?

- 🔰 Negative indexes
- 🔰 Blog post
- 🔰 Remove iterations after blog post
- 🔰 Write readme
- 🔰 Go through each codec and note it in readme (from tuple is interesting)
- 🔰 Fix the docs of each old Num op since Signed & Unsigned replaced Num
